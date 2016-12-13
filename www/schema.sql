-- blog table schema

DROP DATABASE IF EXISTS `test`;

CREATE DATABASE `test`;
USE `test`;

-- 用户表
DROP TABLE IF EXISTS `t_users`;
CREATE TABLE `t_users`(
    `id` VARCHAR(50) NOT NULL,
    `email` VARCHAR(50),
    `name` VARCHAR(20),
    `passwd` VARCHAR(256) NOT NULL,
    `admin` BOOLEAN,
    `avatar` VARCHAR(512),
    `created_at` FLOAT NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 文章表
DROP TABLE IF EXISTS `t_articles`;
CREATE TABLE `t_articles`(
    `id` VARCHAR(50) NOT NULL,
    `user_id` VARCHAR(50) NOT NULL,
    `user_name` VARCHAR(20),
    `user_avatar` VARCHAR(512),
    `title` VARCHAR(256) NOT NULL,
    `summary` VARCHAR(512),
    `content` TEXT,
    `created_at` FLOAT NOT NULL,
    PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 评论表
DROP TABLE IF EXISTS `t_comments`;
CREATE TABLE `t_comments`(
    `id` VARCHAR(50) NOT NULL,
    `user_id` VARCHAR(50) NOT NULL,
    `user_name` VARCHAR(20),
    `user_avatar` VARCHAR(512),
    `article_id` VARCHAR(50) NOT NULL,
    `content` TEXT,
    `created_at` FLOAT NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
