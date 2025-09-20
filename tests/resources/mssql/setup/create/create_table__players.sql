/*
    Purpose:    Creation script for the players testing table.
    Author:     J. Berendt
    Date:       2025-09-20
    Revision:   2

    Updates:
    1:  Written.
    2:  Updated to include a table exists test and UNIQUE constraint.
*/

IF OBJECT_ID('players') IS NULL
BEGIN

    CREATE TABLE [dbilib_test].[dbo].[players] (
        [id]            INTEGER         PRIMARY KEY  IDENTITY(1, 1),
        [guitars_id]    INTEGER         NOT NULL,
        [name]          VARCHAR(250)    NOT NULL
    );

    ALTER TABLE [dbo].[players] ADD CONSTRAINT idx_players_unique UNIQUE ([guitars_id], [name]);

END
