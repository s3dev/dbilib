/*
    Purpose:    Creation script for the players testing table.
    Author:     J. Berendt
    Date:       2023-05-18
    Revision:   1

    Updates:
    1:  Written.
*/


CREATE TABLE IF NOT EXISTS `players` (
    `id`            INTEGER         PRIMARY KEY  AUTO_INCREMENT,
    `guitars_id`    INTEGER         NOT NULL,
    `name`          VARCHAR(250)    NOT NULL
);

ALTER TABLE `players` COMMENT 'Testing table matching a player to their guitar.';

