jQuery(function($) {
    $.widget("ui.dynamicinputs", {
        // Default options
        options: {
            min: 0,
            max: 999999,
            btn_class: 'dynamicinputs-add',
            row_class: 'dynamicinputs-row',
            sample_class: 'dynamicinputs-sample',
            remove_class: 'dynamicinputs-clear'
        },

        _create: function() {
            var self = this,
                clear_selector = '.'+this.options.row_class+' .'+this.options.remove_class;

            this.element.on('click', clear_selector, function(evt) {
                evt.preventDefault();
                var row = $(this).parent(self._rowSelector());
                self.remove(row);
                return false;
            });

            this.element.on('click', '.'+this.options.btn_class, function() {
                self.add();
            });
        },

        /**
         * Check minimum and maximum number of rows allowed
         * @returns {number}
         * @private
         */
        _checkLimits: function()
        {
            var count = this.element.find(this._rowSelector()).length;
            if (count <= this.options.min) return -1;
            if (count >= this.options.max) return 1;
            return 0;
        },

        _rowSelector: function()
        {
            return '.' + this.options.row_class;
        },

        /**
         * Add new row
         */
        add: function()
        {
            // Maximum limit reached
            if (this._checkLimits() > 0)
                return false;

            var last_row = this.element.find(this._rowSelector()).last(),
                new_row = this.element.find('.' + this.options.sample_class).first().clone();

            new_row
                .addClass(this.options.row_class)
                .removeClass(this.options.sample_class);

            // Fix IE bug when placeholder gets copied into textarea value after cloning
            new_row.find("textarea").each(function () {
                if ($(this).val() == $(this).attr("placeholder")) {
                    $(this).val("");
                }
            });

            // Append after last row
            if (last_row.length) {
                new_row.insertAfter(last_row);
            }
            // Insert before "add" button
            else
            {
                var btn = this.element.find('.' + this.options.btn_class);
                new_row.insertBefore(btn);
            }

            this._trigger("added", null, new_row);
            return new_row;
        },

        /**
         * Remove row
         */
        remove: function (row) {
            // Minimum limit reached
            if (this._checkLimits() < 0)
                return false;

            this._trigger("beforedelete", null, row);
            row.remove();
            this._trigger("deleted", null, row);
        }

    });

    // Automatically initialize
    $('.dynamicinputs').each(function(index) {
        var el = $(this);
        el.dynamicinputs({
            min: parseInt(el.data('min')),
            max: parseInt(el.data('max'))
        });
    });
});
