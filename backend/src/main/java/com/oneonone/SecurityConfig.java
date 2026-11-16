package com.oneonone;

import org.springframework.context.annotation.*;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.csrf.HttpSessionCsrfTokenRepository;

@Configuration
public class SecurityConfig {

  @Bean
  PasswordEncoder passwords() {
    return new BCryptPasswordEncoder();
  }

  @Bean
  org.springframework.security.core.userdetails.UserDetailsService users() {
    return name -> {
      throw new org.springframework.security.core.userdetails.UsernameNotFoundException(
        "Use the application sign-in endpoint."
      );
    };
  }

  @Bean
  SecurityFilterChain security(HttpSecurity http) throws Exception {
    return http
      .authorizeHttpRequests(a ->
        a
          .requestMatchers("/api/v1/admin/**")
          .hasRole("ADMIN")
          .requestMatchers(
            "/api/v1/auth/**",
            "/api/v1/system",
            "/api/v1/lessons/**",
            "/api/v1/problems/**",
            "/api/v1/paths",
            "/api/v1/curriculum",
            "/api/v1/search",
            "/api/v1/experiments",
            "/api/v1/challenges/*/attempts",
            "/error"
          )
          .permitAll()
          .anyRequest()
          .authenticated()
      )
      .csrf(c -> c.csrfTokenRepository(new HttpSessionCsrfTokenRepository()))
      .exceptionHandling(e ->
        e
          .authenticationEntryPoint((q, s, x) -> {
            s.setStatus(401);
            s.setContentType("application/json");
            s.getWriter().write(
              "{\"message\":\"Sign in to save your learning and continue.\"}"
            );
          })
          .accessDeniedHandler((q, s, x) -> {
            s.setStatus(403);
            s.setContentType("application/json");
            s.getWriter().write(
              "{\"message\":\"Refresh the page and try again, or sign in with the appropriate account.\"}"
            );
          })
      )
      .build();
  }
}
