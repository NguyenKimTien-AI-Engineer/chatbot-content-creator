-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 29, 2024 at 03:42 AM
-- Server version: 10.11.9-MariaDB
-- PHP Version: 7.2.34

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `social_media_bot`
--

-- --------------------------------------------------------

--
-- Table structure for table `comments`
--

CREATE TABLE `comments` (
  `id` bigint(20) NOT NULL,
  `page_id` varchar(50) NOT NULL,
  `post_id` varchar(50) NOT NULL,
  `comment_id` varchar(50) NOT NULL,
  `parent_comment_id` varchar(50) DEFAULT NULL,
  `user_fb_comment_id` varchar(50) DEFAULT NULL,
  `user_name` varchar(100) DEFAULT NULL,
  `message` text DEFAULT NULL,
  `permalink_url` text DEFAULT NULL,
  `created_time` datetime DEFAULT NULL,
  `is_parent_comment` tinyint(1) DEFAULT 1,
  `page_response` text DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `customer_information`
--

CREATE TABLE `customer_information` (
  `sender_id` varchar(50) NOT NULL,
  `page_id` varchar(50) NOT NULL,
  `information` longtext DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `deposit_transactions`
--

CREATE TABLE `deposit_transactions` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `order_id` varchar(255) NOT NULL,
  `amount` decimal(10,0) NOT NULL,
  `currency` varchar(10) NOT NULL,
  `transaction_type` varchar(50) NOT NULL,
  `payment_method` varchar(50) NOT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` date NOT NULL,
  `updated_at` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `identity`
--

CREATE TABLE `identity` (
  `id` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `info` text DEFAULT NULL,
  `story` text DEFAULT NULL,
  `style_conversation` text DEFAULT NULL,
  `example_conversation` text DEFAULT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Table structure for table `images_post_fb`
--

CREATE TABLE `images_post_fb` (
  `image_id` int(11) NOT NULL,
  `link_images` text NOT NULL,
  `user_id` int(11) NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `images_post_fb`
--

-- --------------------------------------------------------

--
-- Table structure for table `messages`
--

CREATE TABLE `messages` (
  `id` int(11) NOT NULL,
  `sender_id` varchar(255) NOT NULL,
  `page_id` varchar(255) NOT NULL,
  `query` text DEFAULT NULL,
  `response` text DEFAULT NULL,
  `suggest` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`suggest`)),
  `timestamp` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



CREATE TABLE orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_name TEXT NOT NULL,
  unit_price TEXT NOT NULL,
  quantity INT NOT NULL,
  total_price DECIMAL(10, 2) GENERATED ALWAYS AS (CAST(unit_price AS DECIMAL(10, 2)) * quantity) STORED,
  delivery_address TEXT NOT NULL,
  recipient_name TEXT NOT NULL,
  recipient_phone TEXT NOT NULL,
  sender_id TEXT NOT NULL,
  order_status VARCHAR(50) DEFAULT 'Đang xác nhận' CHECK (order_status IN ('Đã xác nhận', 'Đã đóng gói', 'Đang giao', 'Đã giao')),
  customer_note TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);



CREATE TABLE `pages` (
  `fb_page_id` varchar(255) NOT NULL,
  `page_name` varchar(255) NOT NULL,
  `access_token` text NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `access_token_user` text DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE `partners` (
  `partner_id` int(11) NOT NULL,
  `user_name` varchar(255) NOT NULL,
  `user_email` varchar(255) DEFAULT NULL,
  `user_pass` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `role` enum('partner','admin_mekong') DEFAULT 'partner',
  `email_verified` tinyint(1) DEFAULT 0,
  `reset_password_token` varchar(255) DEFAULT NULL,
  `reset_password_expires` datetime DEFAULT NULL,
  `auth_token` varchar(255) DEFAULT NULL,
  `token_expiry` datetime DEFAULT NULL,
  `verification_code` varchar(255) DEFAULT NULL,
  `refresh_token` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `partners` (`partner_id`, `user_name`, `user_email`, `user_pass`, `created_at`, `role`, `email_verified`, `reset_password_token`, `reset_password_expires`, `auth_token`, `token_expiry`, `verification_code`, `refresh_token`) VALUES
(1, 'admin', 'mekongai@gmail.com', '12345678', '2024-11-14 07:09:26', 'partner', 0, NULL, NULL, NULL, NULL, NULL, NULL);

CREATE TABLE `posts` (
  `post_id` int(11) NOT NULL,
  `page_id` varchar(255) DEFAULT NULL,
  `content` text NOT NULL,
  `images` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`images`)),
  `link_post` varchar(255) DEFAULT NULL,
  `post_date` datetime DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `user_id` varchar(255) DEFAULT NULL,
  `status` tinyint(1) NOT NULL DEFAULT 0,
  `link_crontab` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `partner_id` int(11) DEFAULT 1,
  `user_name` varchar(255) NOT NULL,
  `user_email` varchar(255) NOT NULL,
  `user_pass` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `google_id` varchar(255) DEFAULT NULL,
  `email_verified` tinyint(1) DEFAULT 0,
  `reset_password_token` varchar(255) DEFAULT NULL,
  `reset_password_expires` datetime DEFAULT NULL,
  `refresh_token` varchar(255) DEFAULT NULL,
  `token_expiry` datetime DEFAULT NULL,
  `verification_code` varchar(255) DEFAULT NULL,
  `balance` DECIMAL(65,2) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users_facebook`
--

CREATE TABLE `users_facebook` (
  `access_token_user` text NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `name_fb` varchar(255) NOT NULL,
  `id_user_fb` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users_temp`
--

CREATE TABLE `users_temp` (
  `ID` bigint(20) UNSIGNED NOT NULL,
  `user_email` varchar(100) NOT NULL,
  `verification_code` varchar(255) NOT NULL,
  `user_registered` datetime NOT NULL DEFAULT '0000-00-00 00:00:00'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user_tokens`
--

CREATE TABLE `user_tokens` (
  `user_id` int(11) NOT NULL,
  `page_id` varchar(255) NOT NULL,
  `total_tokens` int(11) DEFAULT 0,
  `used_tokens` int(11) DEFAULT 0,
  `remaining_tokens` int(11) GENERATED ALWAYS AS (`total_tokens` - `used_tokens`) STORED
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `_config`
--

CREATE TABLE `_config` (
  `id` varchar(255) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `role` text DEFAULT NULL,
  `target` text DEFAULT NULL,
  `mission` text DEFAULT NULL,
  `note` text DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `id_identity` varchar(255) DEFAULT NULL,
  `id_procedure` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `_managers`
--

CREATE TABLE `_managers` (
  `id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `page_id` varchar(255) DEFAULT NULL,
  `page_name` varchar(255) DEFAULT NULL,
  `files` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`files`)),
  `action` int(11) DEFAULT NULL,
  `config_id` varchar(255) DEFAULT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `_procedures`
--

CREATE TABLE `_procedures` (
  `id` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `_procedure` text DEFAULT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE `tokens` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `user_id` INT(11) NOT NULL,
  `total_tokens` INT NOT NULL,
  `prompt_tokens` INT NOT NULL,
  `completion_tokens` INT NOT NULL,
  `total_cost` DECIMAL(10,2) NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `message` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE `features` (
  `feature_id` INT(11) NOT NULL AUTO_INCREMENT,
  `feature_name` VARCHAR(100) NOT NULL,
  `feature_description` VARCHAR(1000) NOT NULL,
  `feature_path` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`feature_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `features` (`feature_name`, `feature_description`, `feature_path`) VALUES ('user-dashboard', 'user-dashboard', '/user-dashboard');
INSERT INTO `features` (`feature_name`, `feature_description`, `feature_path`) VALUES ('chatbot', 'chatbot', '/chatbot');

CREATE TABLE `user_features` (
  `user_feature_id` INT(11) NOT NULL AUTO_INCREMENT,
  `user_id` INT(11) NOT NULL,
  `list_feature_id` VARCHAR(200) NOT NULL,
  `is_enabled` TINYINT(1) DEFAULT 0,
  `create_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_feature_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE user_profile (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name TEXT NOT NULL,
  gender TEXT NOT NULL,
  phone_number TEXT,
  age TINYINT UNSIGNED,
  hobbies TEXT,
  favorite_color TEXT,
  style_preference TEXT,
  interested_products TEXT,
  sender_id TEXT,
  page_id TEXT
);



--
-- Dumping data for table `_procedures`
--

--
-- Indexes for dumped tables
--

--
-- Indexes for table `comments`
--
ALTER TABLE `comments`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `customer_information`
--
ALTER TABLE `customer_information`
  ADD PRIMARY KEY (`sender_id`,`page_id`);

--
-- Indexes for table `deposit_transactions`
--
ALTER TABLE `deposit_transactions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `order_id` (`order_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `identity`
--
ALTER TABLE `identity`
  ADD PRIMARY KEY (`id`,`user_id`),
  ADD KEY `fk_user_id` (`user_id`);

--
-- Indexes for table `images_post_fb`
--
ALTER TABLE `images_post_fb`
  ADD PRIMARY KEY (`image_id`),
  ADD KEY `fk_user_id_` (`user_id`);

--
-- Indexes for table `messages`
--
ALTER TABLE `messages`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `pages`
--
ALTER TABLE `pages`
  ADD PRIMARY KEY (`fb_page_id`);

--
-- Indexes for table `partners`
--
ALTER TABLE `partners`
  ADD PRIMARY KEY (`partner_id`),
  ADD UNIQUE KEY `user_email` (`user_email`);

--
-- Indexes for table `posts`
--
ALTER TABLE `posts`
  ADD PRIMARY KEY (`post_id`),
  ADD KEY `page_id` (`page_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `user_email` (`user_email`),
  ADD KEY `partner_id` (`partner_id`);

--
-- Indexes for table `users_facebook`
--
ALTER TABLE `users_facebook`
  ADD PRIMARY KEY (`id_user_fb`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users_temp`
--
ALTER TABLE `users_temp`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `user_tokens`
--
ALTER TABLE `user_tokens`
  ADD PRIMARY KEY (`user_id`,`page_id`),
  ADD KEY `page_id` (`page_id`);

--
-- Indexes for table `_config`
--
ALTER TABLE `_config`
  ADD PRIMARY KEY (`id`,`user_id`),
  ADD KEY `fk_config_user_id` (`user_id`);

--
-- Indexes for table `_managers`
--
ALTER TABLE `_managers`
  ADD PRIMARY KEY (`id`,`user_id`),
  ADD KEY `fk_config_user_id__` (`user_id`);

--
-- Indexes for table `_procedures`
--
ALTER TABLE `_procedures`
  ADD PRIMARY KEY (`id`,`user_id`),
  ADD KEY `fk_procedures_id` (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `comments`
--
ALTER TABLE `comments`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=99;

--
-- AUTO_INCREMENT for table `deposit_transactions`
--
ALTER TABLE `deposit_transactions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `images_post_fb`
--
ALTER TABLE `images_post_fb`
  MODIFY `image_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `messages`
--
ALTER TABLE `messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1009;

--
-- AUTO_INCREMENT for table `partners`
--
ALTER TABLE `partners`
  MODIFY `partner_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `posts`
--
ALTER TABLE `posts`
  MODIFY `post_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=108;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=46;

--
-- AUTO_INCREMENT for table `users_temp`
--
ALTER TABLE `users_temp`
  MODIFY `ID` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=57;

--
-- AUTO_INCREMENT for table `_managers`
--
ALTER TABLE `_managers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=299;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `deposit_transactions`
--
ALTER TABLE `deposit_transactions`
  ADD CONSTRAINT `deposit_transactions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `identity`
--
ALTER TABLE `identity`
  ADD CONSTRAINT `fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `images_post_fb`
--
ALTER TABLE `images_post_fb`
  ADD CONSTRAINT `fk_user_id_` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `posts`
--
ALTER TABLE `posts`
  ADD CONSTRAINT `posts_ibfk_1` FOREIGN KEY (`page_id`) REFERENCES `pages` (`fb_page_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `users_ibfk_1` FOREIGN KEY (`partner_id`) REFERENCES `partners` (`partner_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `users_facebook`
--
ALTER TABLE `users_facebook`
  ADD CONSTRAINT `users_facebook_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `user_tokens`
--
ALTER TABLE `user_tokens`
  ADD CONSTRAINT `user_tokens_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `user_tokens_ibfk_2` FOREIGN KEY (`page_id`) REFERENCES `pages` (`fb_page_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `_config`
--
ALTER TABLE `_config`
  ADD CONSTRAINT `fk_config_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `_managers`
--
ALTER TABLE `_managers`
  ADD CONSTRAINT `fk_config_user_id__` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `_procedures`
--
ALTER TABLE `_procedures`
  ADD CONSTRAINT `fk_procedures_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
