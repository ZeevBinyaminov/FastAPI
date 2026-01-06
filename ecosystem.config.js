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
        RUN_MIGRATIONS: "1",
      },
    },
  ],
};
