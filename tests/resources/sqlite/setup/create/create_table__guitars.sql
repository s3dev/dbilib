/*
    Purpose:    Creation script for the guitars testing table.
    Author:     J. Berendt
    Date:       2023-06-07
    Revision:   1

    Updates:
    1:  Written.
*/


CREATE TABLE IF NOT EXISTS `guitars` (
    `id`        INTEGER         PRIMARY KEY  AUTOINCREMENT,
    `make`      VARCHAR(25)     NOT NULL,
    `model`     VARCHAR(25)     NOT NULL,
    `colour`    VARCHAR(25)     NOT NULL
);

