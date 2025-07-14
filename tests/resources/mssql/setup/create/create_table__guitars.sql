/*
    Purpose:    Creation script for the guitars testing table.
    Author:     J. Berendt
    Date:       2025-07-14
    Revision:   1

    Updates:
    1:  Written.
*/


CREATE TABLE [dbilib_test].[dbo].[guitars] (
    [id]        INTEGER         PRIMARY KEY  IDENTITY(1, 1),
    [make]      VARCHAR(25)     NOT NULL,
    [model]     VARCHAR(25)     NOT NULL,
    [colour]    VARCHAR(25)     NOT NULL
);

