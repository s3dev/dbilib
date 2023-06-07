/*
    Purpose:    Creation script for the guitars testing table.
    Author:     J. Berendt
    Date:       2023-05-17
    Revision:   1

    Updates:
    1:  Written.
*/


CREATE TABLE IF NOT EXISTS `guitars` (
    `id`        INTEGER         PRIMARY KEY  AUTO_INCREMENT,
    `make`      VARCHAR(25)     NOT NULL,
    `model`     VARCHAR(25)     NOT NULL,
    `colour`    VARCHAR(25)     NOT NULL
);

ALTER TABLE `guitars` COMMENT 'Testing table listing various guitar models.';

