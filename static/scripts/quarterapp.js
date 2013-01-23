/*

quarterapp.js

*/
(function() {
    "use strict";

    function Quarterapp() {
        this.init();
    };

    Quarterapp.prototype = {
        constructor : Quarterapp,
        activity_markup : '<div class="activity-module"data-activity-id="{0}"><div class="activity-color" style="background-color: #{2};"><span>&nbsp;</span></div><div class="activity-title">{1}</div><div class="activity-edit-title"><input type="text" value="{1}" /></div><div class="activity-control activity-edit-control"><a  href="quarterapp.edit_activity({0});" title="Edit"><span>&nbsp;</span></a></div><div class="activity-control activity-save-control"><a  href="quarterapp.save_activity({0});" title="Save"><span>&nbsp;</span></a></div><div class="activity-control activity-delete-control"><a href="quarterapp.delete_activity({0});" title="Delete"><span>&nbsp;</span></a></div></div>',

        init : function() {
            $("#create-activity").submit($.proxy(this.on_create_activity, this));
            $("div.activity-edit-control > a").click($.proxy(this.on_edit_activity, this));
            $("div.activity-save-control > a").click($.proxy(this.on_save_activity, this));
            $("div.activity-delete-control > a").click($.proxy(this.on_delete_activity, this));
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

            // TODO Need to check form contains any validation error
            
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
            }
            return false;
        },

        on_save_activity : function() {
            var $module = $(event.target).parents("[data-activity-id]");
            if($module.length > 0) {
                var id = $module.attr("data-activity-id");

                // TODO PUT new data to server, if all ok remove edit lcass
                $("[data-activity-id='" + id + "']").removeClass("edit");
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
                        quarterapp.log("Could not delete activity!");
                    }
                });
            }
            return false;
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
