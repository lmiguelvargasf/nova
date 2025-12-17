FROM mcr.microsoft.com/playwright:v1.52.0-noble

# Install Taskfile
RUN sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d
ENV PATH="${PATH}:/app/bin"

WORKDIR /app

RUN corepack enable \
  && corepack prepare pnpm@latest --activate
COPY .npmrc package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install

COPY . .

CMD ["pnpm", "run", "dev", "--hostname", "0.0.0.0"]
