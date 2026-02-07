# Todo App Frontend

A modern, responsive todo application built with Next.js 16, TypeScript, and Tailwind CSS.

## Features

- User authentication (sign up/log in)
- Task management (create, read, update, delete)
- Dark/light theme toggle
- Responsive design for all device sizes
- Secure JWT-based authentication

## Tech Stack

- Next.js 16 (App Router)
- TypeScript
- Tailwind CSS
- Better Auth for authentication
- Axios for API requests

## Getting Started

### Prerequisites

- Node.js 18 or higher
- npm or yarn

### Installation

1. Clone the repository
2. Navigate to the frontend_new directory
3. Install dependencies:

```bash
npm install
```

4. Set up environment variables:

Create a `.env.local` file in the root of the project with the following:

```env
NEXT_PUBLIC_API_BASE_URL=https://your-backend-api-url.com
```

5. Run the development server:

```bash
npm run dev
```

Open [http://localhost:3001](http://localhost:3001) with your browser to see the application.

## Available Scripts

- `npm run dev` - Starts the development server
- `npm run build` - Builds the application for production
- `npm run start` - Starts the production server
- `npm run lint` - Runs ESLint

## Deployment

This application can be deployed on Vercel or GitHub Pages. Choose the option that best fits your needs.

### Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-repo/todo-app-frontend)

Or manually:

1. Install the Vercel CLI:

```bash
npm i -g vercel
```

2. Run the deployment command:

```bash
vercel --prod
```

### Deploy to GitHub Pages

To deploy to GitHub Pages:

1. Build the static version of the app:

```bash
npm run build-gh-pages
```

2. Move the output to the `docs` folder (GitHub Pages default):

```bash
mv out docs
```

3. Commit and push the changes:

```bash
git add docs/
git commit -m "Deploy frontend to GitHub Pages"
git push origin root
```

4. In your GitHub repository settings:
   - Go to the "Pages" section
   - Set source to "Deploy from a branch"
   - Select "root" branch and "/docs" folder

5. Your site will be available at: https://qadirkhan9.github.io/Todo-app-website/

Alternatively, you can run the automated deployment script:

```bash
./deploy-to-gh-pages.sh
```

## Environment Variables

- `NEXT_PUBLIC_API_BASE_URL` - The URL of your backend API (for your deployment: `https://qadirk-todo-app-website.hf.space`)

## Project Structure

```
src/
├── app/              # Next.js App Router pages
├── components/       # Reusable React components
├── context/          # React context providers
├── hooks/            # Custom React hooks
├── lib/              # Utility functions and services
├── services/         # API service implementations
├── styles/           # Global styles
└── types/            # TypeScript type definitions
```

## API Integration

The application integrates with a backend API for user authentication and task management. The API endpoints are configured via the `NEXT_PUBLIC_API_BASE_URL` environment variable.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.
