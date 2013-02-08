/*

 jQuery palette - simple color picker based on the Tango theme colours (http://tango.freedesktop.org/).

 Copyright (c) 2013 Markus Eliasson, https://github.com/eliasson/jquery-plugins/
 
 Released under BSD License

 ----

 <input type="text" class="color-palette" />

 The color value will be written as RGB to the elements attribute  data-colorpicker-value and the elements
 background color will be set to the same color.

 Palette will open on click.

*/
(function($) {
    "use strict";

    var Palette = function(element, options) {
        this.$element = $(element),
        this.options = $.extend({}, $.fn.palette.defaults, options);
        this.$label = $(element).siblings('label'),
        this.palette_code = '<div class="color-palette"></div>';
        this.visible = false;
        this.init();
    }

    Palette.prototype = {
        constructor : Palette,

        init : function() {
            this.$element.on('click', $.proxy(this.show, this));
        },

        show : function(event) {
            var self = this;
            event.stopPropagation();

            if(this.visible) {
                return;
            }

            this.$element.after(this.palette_code);

            var palette = this.$element.siblings('.color-palette'),
                position = this.$element.position(),
                top = position.top + this.$element.height() + 10,
                left = position.left;

            palette.click(function(event){
                event.stopPropagation();
            });

            for(var i = 0; i < this.options.palette.length ; i++) {
                palette.append('<div class="palette-color" style="background-color:#' + this.options.palette[i] + '"></div>');
            }

            palette.css({
                'top': top,
                'left': left
            }).fadeIn('fast');

            this.visible = true;

            $('html').click(function() {
                $(palette).fadeOut('fast', function() {
                    $(palette).remove();
                    self.visible = false;
                });
            });

            $('.palette-color').on('click', function() {
                var color = $(this).css('background-color');
                self.$element.css('color', color);
                self.$element.css('background-color', color);
                self.$element.attr('data-colorpicker-value', color);
                self.$element.val(color);
                $(palette).fadeOut('fast', function() {
                    $(palette).remove();
                    self.visible = false;
                });
            });
        }
    };

    $.fn.palette = function(options) {
        return this.each(function() {
            var $this = $(this),
                data = $this.data('palette');
            if(!data) {
                $this.data('palette', (data = new Palette(this, options)));
            }
        });
    }

    $.fn.palette.Constructor = Palette;

    $.fn.palette.defaults = {
        /* An array of the color codes to display, default is tango palette. */
        palette : ['fce94f', 'edd400', 'c4a000',
            'fcaf3e', 'f57900', 'ce5c00',
            'e9b96e', 'c17d11', '8f5902',
            '8ae234', '73d216', '4e9a06',
            '729fcf', '3465a4', '204a87',
            'ad7fa8', '75507b', '5c3566',
            'ef2929', 'cc0000', 'a40000',
            '888a85', '555753', '2e3436']
    };

    $(document).ready(function() {
        $("input.palette").palette();;
    });
})(jQuery);
