# User Profile Feature

## Overview
User profile management with customizable fields and avatar support.

## Components
- Profile view page
- Edit profile form
- Avatar upload (AWS S3)
- Profile privacy settings

## Dependencies
- Auth feature (must be logged in)
- AWS S3 for image storage
- Image processing library (Pillow)

## Technical Details
- Profile data stored in PostgreSQL
- Avatar images max 5MB
- Supported formats: JPG, PNG, GIF
