package com.oneonone;

import java.util.Map;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestControllerAdvice
public class ApiErrors {

  @ExceptionHandler(ResponseStatusException.class)
  ResponseEntity<?> status(ResponseStatusException e) {
    return ResponseEntity.status(e.getStatusCode()).body(
      Map.of(
        "message",
        e.getReason() == null
          ? "The request could not be completed."
          : e.getReason()
      )
    );
  }

  @ExceptionHandler({
    IllegalArgumentException.class,
    org.springframework.http.converter.HttpMessageNotReadableException.class,
  })
  ResponseEntity<?> invalid(Exception e) {
    return ResponseEntity.badRequest().body(
      Map.of(
        "message",
        e instanceof IllegalArgumentException
          ? e.getMessage()
          : "Check the supplied data and try again."
      )
    );
  }

  @ExceptionHandler(Exception.class)
  ResponseEntity<?> unexpected(Exception e) {
    org.slf4j.LoggerFactory.getLogger(ApiErrors.class).error(
      "Request failed: {}",
      e.getClass().getSimpleName()
    );
    return ResponseEntity.internalServerError().body(
      Map.of(
        "message",
        "Something went wrong. Your saved work is safe; please try again."
      )
    );
  }
}
