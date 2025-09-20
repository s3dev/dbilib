/*
    Purpose:    Creation script for the guitars testing table.
    Author:     J. Berendt
    Date:       2025-09-20
    Revision:   2

    Updates:
    1:  Written.
    2:  Updated to include a table exists test and UNIQUE constraint 
        in support of duplicate INSERT testing.
*/

IF OBJECT_ID('guitars') IS NULL
BEGIN

    CREATE TABLE [dbilib_test].[dbo].[guitars] (
        [id]        INTEGER         PRIMARY KEY  IDENTITY(1, 1),
        [make]      VARCHAR(25)     NOT NULL,
        [model]     VARCHAR(25)     NOT NULL,
        [colour]    VARCHAR(25)     NOT NULL
    );

    ALTER TABLE [dbo].[guitars] ADD CONSTRAINT idx_guitars_unique UNIQUE ([make], [model], [colour]);

END
