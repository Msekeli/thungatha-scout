-- Purge previously collected vacancies without South African location evidence.
-- Employer and source records remain untouched, including companies with zero local jobs.
WITH normalized AS (
    SELECT id,
           regexp_replace(lower(coalesce(location_text, '')), '[^a-z0-9]+', ' ', 'g') AS location
    FROM vacancies
)
DELETE FROM vacancies v
USING normalized n
WHERE v.id = n.id
  AND NOT (
      n.location ~ '(^| )(south africa|western cape|eastern cape|northern cape|kwazulu natal|kwa zulu natal|free state|gauteng|north west|limpopo|mpumalanga|cape town|stellenbosch|durbanville|bellville|brackenfell|kraaifontein|kuils river|parow|goodwood|milnerton|century city|table view|blouberg|somerset west|gordons bay|paarl|wellington|franschhoek|worcester|george|mossel bay|oudtshoorn|knysna|hermanus|malmesbury|saldanha|johannesburg|joburg|pretoria|tshwane|sandton|midrand|centurion|randburg|soweto|durban|pietermaritzburg|richards bay|newcastle|port elizabeth|gqeberha|east london|mthatha|bloemfontein|kimberley|polokwane|nelspruit|mbombela|rustenburg|potchefstroom)( |$)'
  );

CREATE INDEX IF NOT EXISTS vacancies_south_africa_location_idx
    ON vacancies (location_text)
    WHERE status = 'active' AND archived_at IS NULL;
