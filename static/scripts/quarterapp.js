/*

quarterapp.js

*/
(function() {
    "use strict";

    function Quarterapp() {
        // Constructor
    };

    var quarterapp = new Quarterapp();

    quarterapp.log = function(msg) {
        if(console.log !== undefined) {
            console.log(msg);
        }

        return this;
    };

    window.quarterapp = quarterapp;
})();
