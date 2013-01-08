/*

quarterapp.admin.js

Functions specific to the administrator mode

*/
(function($) {
    "use strict";

    function Admin() {
    };

    var admin = new Admin();

    admin.disable_user = function(element, username) {
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
        return admin;
    };

    admin.enable_user = function(element, username) {
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
        return admin;
    };

    admin.delete_user = function(element, username) {
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
        return admin;
    };

    window.quarterapp.admin = admin; // Crash if quarterapp is not defined!
})(jQuery);
