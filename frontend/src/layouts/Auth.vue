<template>
  <div class="login">
    <div class="login__brand">
      <div class="telegram-logo"></div>
    </div>
    <div class="login__form">
      <slot></slot>
    </div>
  </div>
</template>
<style>
  .login {
    width: 100%;
    height: 100%;
    background-color: #36aee2;
    position: absolute;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .login__form {
    background-color: #ffffff;
    box-shadow: 0 1.5px 3px 0 rgba(21, 89, 107, 0.14);
    max-width: 542px;
    width: 100%;
    min-height: 311px;
    margin: auto;
    box-sizing: content-box;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-around;
  }

  .login__form label {
    font-family: 'Roboto', sans-serif;
    font-weight: 300;
  }

  .login__brand {
    margin-top: 20px;
    width: 250px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .login__brand-name {
    font-size: 16pt;
    color: white;
    font-weight: bold;
  }

  .telegram-logo {
    margin-right: 10px;
    background-image: url("../assets/logo_samfeeds_auth.png");
    background-size: cover;
    display: inline-block;
  }
</style>
