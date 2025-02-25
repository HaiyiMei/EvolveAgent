# Evolve Agent Frontend

A modern web interface for the Evolve Agent workflow generator.

## Features

- Modern, responsive UI built with Next.js and Chakra UI
- Real-time logging and progress tracking
- Error handling and notifications
- Dark mode by default

## Setup

1. Install dependencies:
```bash
npm install
# or
yarn install
```

2. Create a `.env.local` file in the frontend directory:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

3. Start the development server:
```bash
npm run dev
# or
yarn dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Development

- `npm run dev` - Start the development server
- `npm run build` - Build for production
- `npm run start` - Start the production server
- `npm run lint` - Run ESLint

## Project Structure

- `src/app/` - Next.js app directory
  - `layout.tsx` - Root layout with Chakra UI provider
  - `page.tsx` - Main page component
  - `providers.tsx` - Chakra UI provider setup

## API Integration

The frontend communicates with the Evolve Agent backend API at `http://localhost:8000/api/v1`. Make sure the backend server is running before using the frontend.

## Environment Variables

- `NEXT_PUBLIC_API_URL` - Backend API URL (default: http://localhost:8000/api/v1)
