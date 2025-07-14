/*
    Purpose:    Creation script for the players testing table.
    Author:     J. Berendt
    Date:       2025-07-14
    Revision:   1

    Updates:
    1:  Written.
*/


CREATE TABLE [dbilib_test].[dbo].[players] (
    [id]            INTEGER         PRIMARY KEY  IDENTITY(1, 1),
    [guitars_id]    INTEGER         NOT NULL,
    [name]          VARCHAR(250)    NOT NULL
);

