CREATE TABLE challenge_attempts (
  id VARCHAR(64) PRIMARY KEY,
  member_id VARCHAR(64) NOT NULL,
  request_id VARCHAR(128) NOT NULL,
  challenge_id VARCHAR(128) NOT NULL,
  lesson_id VARCHAR(128) NOT NULL,
  kind VARCHAR(32) NOT NULL,
  answer_json TEXT NOT NULL,
  correct BOOLEAN NOT NULL,
  feedback TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(member_id, request_id)
);
CREATE INDEX attempts_member_lesson ON challenge_attempts(member_id, lesson_id);
CREATE TABLE learning_events (
  id VARCHAR(64) PRIMARY KEY,
  member_id VARCHAR(64) NOT NULL,
  kind VARCHAR(32) NOT NULL,
  source_id VARCHAR(128) NOT NULL,
  activity_day VARCHAR(10) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX events_member_day ON learning_events(member_id, activity_day);
CREATE TABLE solved_credits (
  member_id VARCHAR(64) NOT NULL,
  problem_id VARCHAR(128) NOT NULL,
  submission_id VARCHAR(128) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(member_id, problem_id)
);
