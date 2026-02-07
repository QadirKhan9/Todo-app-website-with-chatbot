# Todo App Website - Frontend

This is the frontend for the Todo application built with Next.js.

## Deployment to GitHub Pages

To deploy this application to GitHub Pages, follow these steps:

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

## Development

To run the development server:

```bash
npm run dev
```

Open [http://localhost:3001](http://localhost:3001) with your browser to see the result.

## Building for Production

To build the application for production:

```bash
npm run build
```

The optimized production-ready app will be in the `.next` directory.