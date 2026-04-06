/* 1. Create the database if it doesn't exist */
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'DemoDB')
BEGIN
  CREATE DATABASE [DemoDB];
END
GO

USE [DemoDB];
GO

/* 2. Create the table if it doesn't exist */
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Employees]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[Employees](
        [Id] [int] IDENTITY(1,1) NOT NULL,
        [Name] [nvarchar](max) NULL,
        [Email] [nvarchar](max) NULL,
        [Address] [nvarchar](max) NULL,
        [EmpImagePath] [nvarchar](max) NULL,
        CONSTRAINT [PK_Employees] PRIMARY KEY CLUSTERED ([Id] ASC)
    ) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY];
END
GO

/* 3. Insert the data */
SET IDENTITY_INSERT [dbo].[Employees] ON;

-- Using a check to prevent duplicate inserts if the script runs twice
IF NOT EXISTS (SELECT 1 FROM [dbo].[Employees] WHERE [Id] = 3)
BEGIN
    INSERT [dbo].[Employees] ([Id], [Name], [Email], [Address], [EmpImagePath]) VALUES 
    (3, N'Arham1', N'arham@gmail.com', N'Tehsil1', N'/uploads/3168f3a0-6962-4085-b403-e0d1ac3a0a6b_MyPic.jpeg'),
    (5, N'Maida Rehman', N'maida@example.com', N'Pakistan Rawalpindi1', NULL),
    (7, N'Merva Rehman', N'mervarehman@gmail.com', N'Pakistan Rawalpindi', NULL),
    (8, N'Pagenated', N'pagination@gmail.com', N'Paginated Address', NULL),
    (1005, N'Qalab Abbas', N'qalabjunjua@gmail.com', N'Pakistan Rawalpindi', NULL),
    (1007, N'Saad', N'hassan@gmail.com', N'KSA Riyadh Harra', NULL),
    (2004, N'QQ', N'qq@gmail.com', N'123 Main Street23', NULL),
    (2005, N'QQQ', N'qq@gmail.com', N'Pakistan Rawat1', NULL),
    (2006, N'Abbas', N'a@gmail.com', N'Olaya Riyadh', NULL),
    (2007, N'Image Employee', N'img@gmail.com', N'Paginated Address', N'/uploads/76963475-ac68-4073-89e3-7237894cac13_Emp.png');
END

SET IDENTITY_INSERT [dbo].[Employees] OFF;
GO
