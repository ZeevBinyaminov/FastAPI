module.exports = {
  apps: [
    {
      name: "fastapi",
      script: "./app.sh",
      cwd: ".",
      env: {
        APP_HOST: "127.0.0.1",
        APP_PORT: "8000",
        NGINX_SETUP: "0",
        STOP_DB_ON_EXIT: "0",
        INSTALL_REQUIREMENTS: "0",
        RUN_MIGRATIONS: "0",
        PG_HOST: "localhost",
        PG_PORT: "5433",
        PG_USER: "postgres",
        PG_PASSWORD: "postgres",
        PG_DB: "postgres",
        PG_SSL: "disable",
        JWT_SECRET_KEY: "change_me",
        JWT_ALGORITHM: "HS256",
        JWT_EXPIRES_MINUTES: "60",
        ADMIN_USERNAME: "admin",
        ADMIN_PASSWORD: "admin",
      },
    },
  ],
};
