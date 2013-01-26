/*

quarterapp.js

*/
(function() {
    "use strict";

    function Quarterapp() {
        this.current_date = undefined;
        this.init();
    };

    Quarterapp.prototype = {
        constructor : Quarterapp,
        activity_markup : '<div class="activity-module" data-activity-id="{0}"><div class="activity-color" data-palette-value="{2}"><input class="palette" type="text" value="" style="background-color: {2};" disabled /></div><div class="activity-title">{1}</div><div class="activity-edit-title"><input type="text" value="{1}" /></div><div class="activity-control activity-edit-control"><a href="#" title="Edit"><span>&nbsp;</span></a></div><div class="activity-control activity-save-control"><a href="#" title="Save"><span>&nbsp;</span></a></div><div class="activity-control activity-cancel-control"><a  href="#" title="Cancel"><span>&nbsp;</span></a></div><div class="activity-control activity-delete-control"><a href="#" title="Delete"><span>&nbsp;</span></a></div></div>',

        init : function() {
            // Activity controls
            $("#create-activity").submit($.proxy(this.on_create_activity, this));
            $("div.activity-edit-control > a").click($.proxy(this.on_edit_activity, this));
            $("div.activity-cancel-control > a").click($.proxy(this.on_cancel_activity, this));
            $("div.activity-save-control > a").click($.proxy(this.on_save_activity, this));
            $("div.activity-delete-control > a").click($.proxy(this.on_delete_activity, this));

            // Sheet date control
            var current_date = $("#sheet").attr("data-sheet-date");
            this.current_date = new Date(current_date);
            var picker = new Pikaday({
                field: document.getElementById('datepicker'),
                firstDay : 1,
                defaultDate : this.current_date,
                setDefaultDate : true,
                onSelect: $.proxy(this.on_select_date, this)
            });
        },

        log : function(msg) {
            if(console.log !== undefined) {
                console.log(msg);
            }
        },

        /**
         * Callback when user tries to create an activity using the form.
         */
        on_create_activity : function(event) {
            var self = this,
                $form = $(event.target);
            event.preventDefault();

            if($form.attr("data-validation-result") == "not-valid") {
                return;
            }
            
            var data = $form.serialize();

            $.ajax({
                url : $form.attr("action"), 
                type : $form.attr("method"),
                data : data,
                success : function(data, status, jqXHR) {
                    $form.find("input").val("");
                    $form.find("div.error-message").remove();

                    var new_activity = self.activity_markup.format(data.activity.id, data.activity.title, data.activity.color);
                    $("[data-activity-list]").append(new_activity);
                },
                error : function(jqXHR, status, errorThrown) {
                    if($form.find("div.error-message").length === 0) {
                        $form.append('<div class="error-message note"><p>Could not create activity!</p></div>');
                    }
                }
            });
        },

        on_edit_activity : function(event) {
            var $module = $(event.target).parents("[data-activity-id]");
            if($module.length > 0) {
                var id = $module.attr("data-activity-id");
                $("[data-activity-id='" + id + "']").addClass("edit");
                $module.find("input.palette").prop('disabled', false);
            }
            return false;
        },

        on_cancel_activity : function() {
            var $module = $(event.target).parents("[data-activity-id]");
            if($module.length > 0) {
                var id = $module.attr("data-activity-id");
                // Restore old values
                var title = $module.find("div.activity-title").text(),
                    color = $module.find("div.activity-color[data-palette-value]").attr("data-palette-value");
                $module.find("div.activity-edit-title > input").val(title);
                $module.find("input.palette").css("background-color", color);


                $("[data-activity-id='" + id + "']").removeClass("edit");
                $module.find("input.palette").prop('disabled', true);
            }
            return false;
        },

        on_save_activity : function() {
            var $module = $(event.target).parents("[data-activity-id]");
            if($module.length > 0) {
                var id = $module.attr("data-activity-id"),
                    title = $module.find("div.activity-edit-title > input").val(),
                    color = $module.find("input.palette").css("background-color");

                $.ajax({
                    url : "/api/activity/" + id,
                    type : "PUT",
                    data : {
                        "title" : title,
                        "color" : color
                    },
                    success : function(data, status, jqXHR) {
                        
                        $module.find("div.activity-title").text(title);
                        $module.find("div.activity-color[data-palette-value]").attr("data-palette-value", color);

                        $("[data-activity-id='" + id + "']").removeClass("edit");
                    },
                    error : function(jqXHR, status, errorThrown) {
                        // TODO Error dialog
                        quarterapp.log("Could not delete activity!");
                    }
                });
            }
            return false;
        },

        on_delete_activity : function() {
            var $module = $(event.target).parents("[data-activity-id]");
            if($module.length > 0) {
                var id = $module.attr("data-activity-id");
                $.ajax({
                    url : "/api/activity/" + id,
                    type : "DELETE",
                    success : function(data, status, jqXHR) {
                        $module.remove();
                    },
                    error : function(jqXHR, status, errorThrown) {
                        // TODO Error dialog
                        quarterapp.log("Could not delete activity!");
                    }
                });
            }
            return false;
        },

        on_select_date : function(date) {
            if((date.getFullYear() === this.current_date.getFullYear()) &&
                (date.getMonth() === this.current_date.getMonth()) &&
                (date.getDate() === this.current_date.getDate())) {
                return;
            }

            var month = (date.getMonth() + 1).toString();
            if(month.length === 1) {
                month = "0" + month;
            }

            var day = date.getDate().toString();
            if(day.length === 1) {
                day = "0" + day;
            }
            var location = "/sheet/{0}-{1}-{2}".format(date.getFullYear(), month, day);
            window.location = location;
        }
    }

    window.quarterapp = new Quarterapp();
})();

/*
 * Add a format function to String that formats a string containing
 * {index} with the given values.
 *
 * E.g.
 * "Hello {0}, nice to meet {1}",format("John", "you");
 *
 * will return the string:
 * "Hello John, nice to meet you"
 */
if(String.prototype.format === undefined) {
    String.prototype.format = function() {
        var formatted = this;
        for(var i = 0; i < arguments.length; i++) {
            var regexp = new RegExp('\\{'+i+'\\}', 'gi');
            formatted = formatted.replace(regexp, arguments[i]);
        }
        return formatted;
    };    
}

/**
 * Make jquery return hex code on background-color instead of rbg
 * From http://stackoverflow.com/questions/6177454/can-i-force-jquery-cssbackgroundcolor-returns-on-hexadecimal-format
 */
$.cssHooks.backgroundColor = {
    get: function(elem) {
        if (elem.currentStyle)
            var bg = elem.currentStyle["backgroundColor"];
        else if (window.getComputedStyle)
            var bg = document.defaultView.getComputedStyle(elem,
                null).getPropertyValue("background-color");
        if (bg.search("rgb") == -1)
            return bg;
        else {
            bg = bg.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
            function hex(x) {
                return ("0" + parseInt(x).toString(16)).slice(-2);
            }
            return "#" + hex(bg[1]) + hex(bg[2]) + hex(bg[3]);
        }
    }
};
