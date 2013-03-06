/*

  Copyright (c) 2013 Markus Eliasson, http://www.quarterapp.com/

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
 
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
 
  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
  
*/
(function() {
    "use strict";

    function Quarterapp() {
        this.current_activity = { "id": -1, "color" : "#fff", "title" : "Not working"};
        this.current_date = undefined;
        this.pending_update = false;
        this.init();
    };

    Quarterapp.prototype = {
        constructor : Quarterapp,
        activity_markup : '<div class="activity-module" data-activity-id="{0}"><div class="activity-color" data-palette-value="{2}"><label class="palette" style="background-color: {2};" data-disabled="true" /></div><div class="activity-title">{1}</div><div class="activity-edit-title"><input type="text" value="{1}" /></div><div class="activity-control activity-edit-control"><a href="#" title="Edit"><span>&nbsp;</span></a></div><div class="activity-control activity-save-control"><a href="#" title="Save"><span>&nbsp;</span></a></div><div class="activity-control activity-cancel-control"><a  href="#" title="Cancel"><span>&nbsp;</span></a></div><div class="activity-control activity-delete-control"><a href="#" title="Delete"><span>&nbsp;</span></a></div></div>',
        summary_markup : '<tr data-activity-id="{0}" style="color: {1};"><td class="value">{2}</td><td class="activity">{3}</td></tr>',

        init : function() {
            // Activity controls
            $("#create-activity").submit($.proxy(this.on_create_activity, this));
            $("div.activity-edit-control > a").click($.proxy(this.on_edit_activity, this));
            $("div.activity-cancel-control > a").click($.proxy(this.on_cancel_activity, this));
            $("div.activity-save-control > a").click($.proxy(this.on_save_activity, this));
            $("div.activity-delete-control > a").click($.proxy(this.on_delete_activity, this));
            
            // Sheet date control
            if($("#datepicker").length > 0) {
                var current_date = $("#sheet").attr("data-sheet-date");
                this.current_date = new Date(current_date);
                var picker = new Pikaday({
                    field: document.getElementById('datepicker'),
                    firstDay : 1,
                    defaultDate : this.current_date,
                    setDefaultDate : true,
                    onSelect: $.proxy(this.on_select_date, this)
                });
            }

            if($("input.datepicker").length > 0 ) {
                var self = this;
                $("input.datepicker").each(function(index, element) {
                    var picker = new Pikaday({
                        field: element,
                        firstDay : 1,
                        setDefaultDate : true,
                        format : "YYYY-MM-DD" /*,
                        onSelect : function(date) {
                            $(element).val(self.to_date_string(date));
                        }*/
                    });
                });
            }
            // Bind palette
            if($().palette) {
                $(".palette").palette();
            }

            // Sheet activity selector
            $("#current-activity").click($.proxy(this.on_toggle_activity_selector, this));
            $("#available-activities div.activity").on("click", $.proxy(this.on_select_activity, this));

            // Only render work hours
            $("table.sheet tr").slice(0, 6).hide();
            $("table.sheet tr").slice(18, 24).hide();

            // Sheet extend controls
            $("#extend-sod").click($.proxy(this.on_extend_sod, this));
            $("#extend-eod").click($.proxy(this.on_extend_eod, this));

            // Sheet marker event
            $("table.sheet td").bind("mousedown", $.proxy(this.on_sheet_mouse_down, this));
            $("table.sheet td").bind("mousemove", $.proxy(this.on_sheet_mouse_move, this));
            $("body").bind("mouseup", $.proxy(this.on_sheet_mouse_up, this));

            // Profile view
            $("#delete-account").click($.proxy(this.on_show_delete_account, this));

            // Set the current activity
            var activity = this.get_preferred_activity();
            this.set_current_activity(activity);

            // Make activities before / after sod/eod visible
            this.show_sheets_activities();
        },

        /**
         * Log message to console
         */
        log : function(msg) {
            if(console.log !== undefined) {
                console.log(msg);
            }
        },

        /**
         * Show an error "dialog" (not modal) at the top of the page
         */
        show_error : function(title, message) {
            $("#main-region")
                .prepend('<div class="error box"><section class="content"><h3>{0}</h3><p>{1}</p><a class="dismiss" href="#" title="Dismiss" data-dismiss-action>dismiss</a></section></div>'.format(title, message));
                $("a.dismiss").bind("click", $.proxy(this.on_dismiss_error, this));
        },

        /**
         * Callback used to dismiss error dialog
         */
        on_dismiss_error : function() {
            var $element = $(event.target);
            $element.parents("div.error.box").fadeOut(300, function() { $(this).remove(); } );
        },

        /**
         * Return the YYYY-MM-DD representation for the given date object.
         */
        to_date_string : function(date) {
            var month = (date.getMonth() + 1).toString();
            if(month.length === 1) {
                month = "0" + month;
            }

            var day = date.getDate().toString();
            if(day.length === 1) {
                day = "0" + day;
            }
            return "{0}-{1}-{2}".format(date.getFullYear(), month, day);
        },

        /**
         * Function used to calculate a darker or lighter shade of a color.
         * hex - The base hex color
         * lum - Percentage luminance to alter
         *
         * Inspired from http://www.sitepoint.com/javascript-generate-lighter-darker-color/
         */
        luminance : function(hex, lum) {
            function from_hex(x) {
                return ("0" + parseInt(x).toString(16)).slice(-2);
            }

            try {
                // validate hex string
                hex = String(hex).replace(/[^0-9a-f]/gi, '');
                if (hex.length < 6) {
                    hex = hex[0]+hex[0]+hex[1]+hex[1]+hex[2]+hex[2]
                }

                lum = lum || 0;

                // convert to decimal and change luminosity
                var rgb = "#", c, i
                for (i = 0; i < 3; i++) {
                    c = parseInt(hex.substr(i*2,2), 16)
                    c = Math.round(Math.min(Math.max(0, c + (c * lum)), 255)).toString(16);
                    rgb += ("00"+c).substr(c.length);
                }
                return rgb;
            }
            catch(e) {
                return hex;
            }
        },

        /**
         * Set the preferred activity to use in the sheet view.
         */
        set_preferred_activity : function(activity) {
            if(typeof(localStorage) != "undefined") {
                localStorage.setItem("quarter-activity-id", activity.id);
                localStorage.setItem("quarter-activity-title", activity.title);
                localStorage.setItem("quarter-activity-color", activity.color);
            }
        },

        /**
         * Get the preferred activity to use as the default activity on the sheet view.
         */
        get_preferred_activity : function() {
            if(typeof(localStorage) != "undefined") {
                return { "id" :  localStorage.getItem("quarter-activity-id"),
                         "title" : localStorage.getItem("quarter-activity-title"),
                         "color" : localStorage.getItem("quarter-activity-color") };
            }
            else {
                return this.current_activity;
            }
        },

        /**
         * In sheet view, show all activities that are used, even if they are before
         * or after start-of-day or end-of-day limit.
         */
        show_sheets_activities : function() {
            var $early_rows = $("table.sheet tbody tr").slice(0, 11),
                $late_rows = $("table.sheet tbody tr").slice(12, 24),
                found_it = false;

            var process_row = function() {
                if(found_it === true) {
                    $current_row.show();
                    return true;
                }
                else if(! $current_row.is(":visible") ) {
                    if($current_row.find("span[data-activity-id!='-1']").length > 0) {
                        $current_row.show();
                        return true;
                    }
                }
            };

            // Go through early rows from start, if one row contains used activity. 
            // Show that row, and all subsequent early rows
            for(var i = 0; i < $early_rows.length; i++) {
                var $current_row = $early_rows.eq(i);
                found_it = process_row($current_row, found_it);
            }

            // Go through late rows from the end, if one row contains a used activity.
            // Show that row and all subsequent rows.
            for(var i = $late_rows.length-1; i > -1; i--) {
                var $current_row = $late_rows.eq(i);
                found_it = process_row($current_row, found_it);
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
                    $(".note#no-activities").remove();
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
                $module.find("label.palette").data('disabled', false);
            }
            return false;
        },

        on_cancel_activity : function(event) {
            var $module = $(event.target).parents("[data-activity-id]");
            if($module.length > 0) {
                var id = $module.attr("data-activity-id");
                // Restore old values
                var title = $module.find("div.activity-title").text(),
                    color = $module.find("div.activity-color[data-palette-value]").attr("data-palette-value");
                $module.find("div.activity-edit-title > input").val(title);
                $module.find("label.palette").css("background-color", color);
                $module.find("label.palette").data('disabled', true);

                $("[data-activity-id='" + id + "']").removeClass("edit");
                
            }
            return false;
        },

        on_save_activity : function(event) {
            var $module = $(event.target).parents("[data-activity-id]");
            if($module.length > 0) {
                var id = $module.attr("data-activity-id"),
                    title = $module.find("div.activity-edit-title > input").val(),
                    color = $module.find("label.palette").css("background-color");
                    $module.find("label.palette").data('disabled', true);
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
                        quarterapp.show_error("Oops", "Could not save activity!");
                    }
                });
            }
            return false;
        },

        on_delete_activity : function(event) {
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
                        quarterapp.show_error("Oops", "Could not delete activity!");
                    }
                });
            }
            return false;
        },

        /**
         * Load a new page when the user selects a different date in the sheet view
         */
        on_select_date : function(date) {
            if((date.getFullYear() === this.current_date.getFullYear()) &&
                (date.getMonth() === this.current_date.getMonth()) &&
                (date.getDate() === this.current_date.getDate())) {
                return;
            }

            var location = "/sheet/" + this.to_date_string(date);
            window.location = location;
        },

        /**
         * Toggle the sheet views activity selector
         */
        on_toggle_activity_selector : function() {
            $("#available-activities").toggle();
        },

        /**
         * Update the current activity when the user selects an activity from the activity selector.
         */
        on_select_activity : function(event) {
            var $element = $(event.target).parents("div.activity");
            var new_id = $element.attr("data-activity-id"),
                new_color = $element.attr("data-activity-color"),
                new_title = $element.attr("data-activity-title");

            if(new_id !== undefined && new_color !== undefined && new_title !== undefined) {
                this.set_current_activity({ "id": new_id, "color" : new_color, "title" : new_title})
            }
            
            $("#available-activities").hide();
        },

        /**
         * Set the current activity in the sheet view, and update the visual representation
         */
        set_current_activity : function(activity) {
            if($('div.activity[data-activity-id="' + activity.id + '"]').length > 0) {
                this.current_activity = activity;
                var $current_activity = $("#current-activity");
                $current_activity.find("label.palette").css("background-color", activity.color);
                $current_activity.find("div.activity-title").text(activity.title)

                this.set_preferred_activity(activity);
            }
        },

        /**
         * Extend the sheet view with an hour at the start of day (if possible)
         */
        on_extend_sod : function() {
            var $rows = $("table.sheet tbody tr").slice(0, 11);
            for(var i = $rows.length-1; i > -1; i--) {
                if(! $rows.eq(i).is(":visible") ) {
                    $rows.eq(i).show();
                    return;
                }
            }
        },

        /**
         * Extend the sheet view with an hour at the end of day (if possible)
         */
        on_extend_eod : function() {
            var $rows = $("table.sheet tbody tr").slice(12, 24);
            for(var i = 0; i < $rows.length; i++) {
                if(! $rows.eq(i).is(":visible") ) {
                    $rows.eq(i).show();
                    return;
                }
            }
        },

        paint_cell : function($activity_cell) {
            var activity_id = $activity_cell.attr("data-activity-id");

            if(activity_id === undefined) {
                return; // Not an activity cell, just ignore.
            }

            // Cell is already updated, just ignore.
            // (this is safe since we only allow one update at a time, it is's painted, it's painted)
            if($activity_cell.attr("data-activity-previous-id") !== undefined) {
                return;
            }

            // Store the old activity id and old color for the activity
            // these will be reused if the update does not succeed.
            $activity_cell.attr("data-activity-previous-id", activity_id);
            $activity_cell.attr("data-activity-previous-color", $activity_cell.css("background-color"));

            // Set new id
            $activity_cell.attr("data-activity-id", this.current_activity.id);

            // Update cells background color and border to new activities color
            $activity_cell.css("background-color", this.current_activity.color);
            $activity_cell.css("border-color", this.luminance(this.current_activity.color, -0.2));

            // Add pending state class (used for visual feedback)
            $activity_cell.addClass("pending");
        },

        /**
         * Setup the activity update "transaction". Nothing will be sent to the server until the
         * mouse is relased and all updated activities are sent at once.
         */
        on_sheet_mouse_down : function(event) {
            if(event.which !== 1) {
                return;
            }

            this.pending_update = true;
            this.paint_cell($(event.target));
        },

        /**
         * Update activity cell if mouse is pressed, keep original values in case of update error.
         * This function does not communicate with the server, all pending updates are accumalated
         * and transmitted at mouse up.
         */
        on_sheet_mouse_move : function(event) {
            if(event.which !== 1) {
                return;
            }

            if(!this.pending_update) {
                return;
            }

            this.paint_cell($(event.target));
        },

        /**
         * Finalize the activity update by issueing an update request to the server. We expect that
         * all goes well (as we already updated UI and state), but if it failes restore to old activities
         * again.
         */
        on_sheet_mouse_up : function(event) {
            function cleanup_pending_activities() {
                var $activities = $("table.sheet span.activity-cell.pending");
                // Remove any temporary attributes
                $activities.removeAttr("data-activity-previous-id");
                $activities.removeAttr("data-activity-previous-color");

                // Remove all pending states
                $activities.removeClass("pending");
            }

            if(event.which !== 1) {
                return;
            }
            if(!this.pending_update) {
                return;
            }

            var self = this;

            // Get all activities from sheet (all 96), regardless of state. Transform the these
            // into a JSON array and PUT that at the server.
            var quarters = []
            var $cells = $("table.sheet span.activity-cell").each(function(index, cell) {
                quarters.push($(cell).attr("data-activity-id"));
            });

            if(quarters.length !== 96) {
                quarterapp.show_error("Oops", "Sheet is broken, try to refresh the page.");
                return;
            }

            // Convert to String instead of Array
            quarters = quarters + "";

            $.ajax({
                    url : "/api/sheet/" + self.to_date_string(self.current_date),
                    type : "PUT",
                    data : {
                        "quarters" : quarters
                    },
                    success : function(data, status, jqXHR) {
                        // If all goes well we have already updated the activity attributes
                        // final cleanup will remove any state class from UI
                        var summary_total = $("#summary-hours"),
                            summary_table = $("#sheet-summary");
                        summary_total.html(new Number(data.total).toFixed(2));
                        summary_table.empty();
                        summary_table.append("<tbody></tbody>");
                        $.each(data.summary, function(index, act) {
                            var ac = self.summary_markup.format(act.id, act.color, new Number(act.sum).toFixed(2), act.title);
                            summary_table.append(ac);
                        });
                    },
                    error : function(jqXHR, status, errorThrown) {
                        var $activities = $("table.sheet span.activity-cell.pending");
                        $("table.sheet span.activity-cell.pending").each(function(index, element) {
                            var $element = $(element);
                            $element.attr("data-activity-id", $element.attr("data-activity-previous-id"));
                            
                            var activity_color = $element.attr("data-activity-previous-color");
                            $element.css("background-color", activity_color);
                            $element.css("border-color", self.luminance(activity_color, -0.2));
                        });
                    }
                });

            cleanup_pending_activities();
            this.pending_update = false;
        },

        on_show_delete_account : function() {
            $("#delete-account-form").show();
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
