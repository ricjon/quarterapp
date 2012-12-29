#
# MySQL script that sets up the necessary tables 
use quarterapp;

CREATE TABLE `activities` (
    `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(64) NOT NULL DEFAULT '',
    `title` VARCHAR(32) NOT NULL DEFAULT '',
    `color` VARCHAR(32) NOT NULL DEFAULT '',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `sheets` (
    `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(64) NOT NULL DEFAULT '',
    `date` DATE NOT NULL,
    `quarters` TEXT NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `settings` (
    `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
    `key` VARCHAR(64) NOT NULL,
    `value` TEXT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


use quarterapp_test;

CREATE TABLE `activities` (
    `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(64) NOT NULL DEFAULT '',
    `title` VARCHAR(32) NOT NULL DEFAULT '',
    `color` VARCHAR(32) NOT NULL DEFAULT '',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `sheets` (
    `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(64) NOT NULL DEFAULT '',
    `date` DATE NOT NULL,
    `quarters` TEXT NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `settings` (
    `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
    `key` VARCHAR(64) NOT NULL,
    `value` TEXT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
