-- Hint use is review evidence: a hinted success repeats its review interval instead of advancing it.
ALTER TABLE challenge_attempts ADD COLUMN hint_used BOOLEAN NOT NULL DEFAULT FALSE;
