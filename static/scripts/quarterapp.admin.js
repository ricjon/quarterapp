/*

quarterapp.admin.js

Functions specific to the administrator mode

*/
(function($) {
    "use strict";

    function Admin() {

    };

    Admin.prototype = {
        constructor : Admin,

        init : function() {

        },

        disable_user : function(element, username) {
            var $element = $(element);
            $.ajax({
                url : $element.attr("href"),
                type : "POST",
                success : function(data, status, jqXHR) {
                    $element.html("enable");
                    $element.attr("href", $element.attr("href").replace("disable", "enable"));
                    $element.attr("onclick", $element.attr("onclick").replace("disable_user", "enable_user"));
                },
                error : function(jqXHR, status, errorThrown) {
                    quarterapp.log("Error on disable");
                }
            });
        },

        enable_user : function(element, username) {
            var $element = $(element);
            $.ajax({
                url : $element.attr("href"),
                type : "POST",
                success : function(data, status, jqXHR) {
                    $element.html("disable");
                    $element.attr("href", $element.attr("href").replace("enable", "disable"));
                    $element.attr("onclick", $element.attr("onclick").replace("enable_user", "disable_user"));
                },
                error : function(jqXHR, status, errorThrown) {
                    quarterapp.log("Error on enable");
                }
            });
        },

        delete_user : function(element, username) {
            $.ajax({
                url : element.href,
                type : "POST",
                success : function(data, status, jqXHR) {
                    $(element).parents("tr").remove();
                },
                error : function(jqXHR, status, errorThrown) {
                    quarterapp.log("Error on enable");
                }
            });
        },

        clear_filter : function() {
            $("#filter").val(""); // Clear the username filter
        },

        toggle_setting : function(element) {
            var $element = $(element);
            var checked = $element.attr("checked");

            $.ajax({
                url : "/admin/settings/" + $element.attr("id"),
                type : "POST",
                data : {
                    "value" : checked == undefined ? 0 : 1
                },
                success : function(data, status, jqXHR) {
                    $element.prop("checked", checked ? true : false);
                },
                error : function(jqXHR, status, errorThrown) {
                    var $desc = $element.parent(".setting-control").siblings(".setting-description");
                    $desc.append('<div class="error-message">Could not change setting!</div>');
                }
            });
        }
    }
    
    if(window.quarterapp === undefined) {
        console.log("Oops, admin script must load after main quarterapp.js");
    }
    else {
        window.quarterapp.admin = new Admin();    
    }
})(jQuery);
