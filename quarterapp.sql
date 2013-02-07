#
# MySQL script that sets up the necessary tables 
use quarterapp;

CREATE TABLE `activities` (
    `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
    `user` INT(11) NOT NULL,
    `title` VARCHAR(32) NOT NULL DEFAULT '',
    `color` VARCHAR(32) NOT NULL DEFAULT '',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `sheets` (
    `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
    `user` INT(11) NOT NULL,
    `date` DATE NOT NULL,
    `quarters` TEXT NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `settings` (
    `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(64) NOT NULL,
    `value` TEXT NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `users` (
    `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(256) NOT NULL DEFAULT '',
    `password` VARCHAR(90) NOT NULL DEFAULT '',
    `type` TINYINT NOT NULL DEFAULT '0',
    `state`  TINYINT NOT NULL DEFAULT '0',
    `last_login` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `reset_code` VARCHAR(64),
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `signups` (
    `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(256) NOT NULL DEFAULT '',
    `activation_code` VARCHAR(64) NOT NULL DEFAULT '',
    `ip` VARCHAR(39) NOT NULL DEFAULT '',
    `signup_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

#
# Insert default settings
INSERT INTO quarterapp.settings (`name`, `value`) VALUES("allow-signups", "1");
INSERT INTO quarterapp.settings (`name`, `value`) VALUES("allow-activations", "1");

#
# Insert default administrator
INSERT INTO quarterapp.users (`username`, `password`, `type`, `state`) VALUES("admin", "", 1, 1);

commit;
#
# type
#  0 = Normal user
#  1 = Administrator
#
# state
#  0 = disabled
#  1 = active 
