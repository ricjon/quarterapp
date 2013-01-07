/*

 jQuery validator - Simple form validation plugin.

 Copyright (c) 2013 Markus Eliasson, https://github.com/eliasson/jquery-plugins/
 
 Released under BSD License

 ----

 Validates a form's input fields either at focus loss or at form submission (default).

 To mark a form for validation, add the attribute "data-validation"
 To add a validator for an input element, add the validation strategy in the input field's
 data-validor attribute (may be a list of space separated strategies).


 <form data-validation>
    <label for="username">Username</label>
    <input type="text" name="username" id="username" 
        data-validator="required email"
        data-validator-on="focus-loss" />
                
    <label for="password">Password</label>
    <input type="password" name="password" id="password"
        data-validator="required password"
        data-validator-on="focus-loss" />
                
    <label for="verify-password">Verify password</label>
    <input type="password" name="verify-password" id="verify-password"
        data-validator="required password mirror"
        data-validator-on="focus-loss"
        data-validator-mirror="password" />
 </form>


    data-validator                  List of validation strategies (space separated)

        required                        Validates that this element contains data

        email                           Validates a simple e-mail address

        password                        Validates a password
                                        Rules are  > 5 chars, 1 digit, 1 lower, 1 upper

        mirror                          Validates this field's value as a mirror. Needs
                                        attribute 'data-validator-mirror'

    data-validator-on               Specifies when validation should occur
        submit (default)                Just before form submission
        focus-loss                      At elements focus loss
    
    data-validator-mirror           Specifies the id of the mirroring field
*/
(function($) {
    "use strict";

    function Validator(form, options, strategies) {
        this.options = $.extend({}, $.fn.validator.defaults, options);
        this.strategies = $.extend({}, $.fn.validator.strategies, strategies);
        this.$form = $(form);
        this.$elements = jQuery();
        this.init();
    }

    Validator.prototype = {
        init : function() {
            var self = this;
            this.$elements = this.$form.find('input[data-validator]');

            this.$form.find('input[data-validator-on="focus-loss"]').each(function(i, e) {
                $(e).blur($.proxy(self.on_blur, self));
            });
            
            this.$form.submit($.proxy(this.on_submit, this));    
        },

        on_blur : function(event) {
            this.validate_element($(event.target));
        },

        on_submit : function(event) {
            console.log("Validate");
            var self = this;

            $.each(this.$elements, function(index, element) {
                self.validate_element($(element));
            });

            if(this.$form.find("input." + self.options.error_class).length > 0) {
                event.preventDefault();    
            }
        },

        validate_element : function($element) {
            var self = this;
            var strategies = $element.attr("data-validator").split(" ");

            $.each(strategies, function(index, element_strategy) {
                var strategy = self.strategies[element_strategy];
                if(strategy !== undefined) {
                    var message = strategy.check(self, $element);
                    if(message !== undefined) {
                        if(!$element.hasClass(self.options.error_class)) {
                            $element.addClass(self.options.error_class);
                        }
                        if($element.siblings("div.error-message").length == 0) {
                            $element.after('<div class="error-message">' + message + '</div>');
                        }
                        return false; // Break each loop
                    }
                    else {
                        // Remove any previous added markup
                        $element.removeClass(self.options.error_class);
                        $element.siblings("div.error-message").remove();
                    }
                }
            });
        }
    };

    $.fn.validator = function(options, strategies) {
        return this.each(function() {
            var $this = $(this),
                data = $this.data("validator"),
                opts = $.extend({}, options),
                stgs = $.extend({}, strategies);

            if(!data) {
                $this.data("validator", (data = new Validator($this, opts, stgs)));
            }
        });
    };

    /* The default options */
    $.fn.validator.defaults = {
        /* The CSS class added to the input fields and form element at validation error */
        error_class : "error"
    };

    /* The supported types of strategies */
    $.fn.validator.strategies = {
        /* Validates that a required field has a value*/
        "required" : {
            check : function(self, $element) {
                var type = $element.attr("type"),
                    valid = false;
                if(type === "checkbox") {
                    valid = $element.attr("checked");
                } 
                else if(type === "text" || type === "password") {
                    valid = $element.val().length > 0;
                }
                return valid ? undefined : "This field is required";
            }
        },

        /* Very simple e-mail validation. */
        "email"    : {
            check : function(self, $element) {
                var type = $element.attr("type"),
                    valid = false;

                if(type === "text") {
                    valid = /\S+@\S+\.\S+/.test($element.val());
                }
                return valid ? undefined : "This is not a valid email adress";
            }
        },

        /* Verify password */
        "password" : {
            check : function(self, $element) {
                var type = $element.attr("type"),
                    valid = false;
                if(type === "password") {
                    /* one digit, one lowercase, one upper case, and >5 in length */
                    var text = $element.val();

                    valid = text.length > 5;
                    if(!valid) {
                        return "Password needs to be more than 5 characters";
                    }
                    
                    valid =    /(?=.*\d)/.test(text);
                    if(!valid) {
                        return "Password needs to contain at least one digit";
                    }

                    valid = /(?=.*[a-z])/.test(text);
                    if(!valid) {
                        return "Password needs to contain at least one lower case character";
                    }

                    valid = /(?=.*[A-Z])/.test(text);
                    if(!valid) {
                        return "Password needs to contain at least one upper case character";
                    }                    
                }
                return undefined; // Should really be an error
            }
        },

        /* Verity this field's value mirrors another field  */
        "mirror" : {
            check : function(self, $element) {
                var mirror = $element.attr("data-validator-mirror");
                if(mirror !== undefined) {
                    var $mirror = self.$form.find("#" + mirror); 
                    if($element.val() !== $mirror.val()) {
                        return "Not matching";
                    }
                }
                return undefined; // Should really be an error
            }
        }
    };

    $.fn.validator.Constructor = Validator;

    /* Automatically wire the validator plugin for all forms marked for validation */
    $(function() {
        $("form[data-validation]").validator();
    });
})(jQuery);
