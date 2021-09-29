CREATE TABLE IF NOT EXISTS labs (id char(1) PRIMARY KEY);

CREATE TABLE IF NOT EXISTS lab_techs (
    id smallint PRIMARY KEY,
    name varchar(512) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS plots (
    lab_id char(1) NOT NULL REFERENCES labs(id),
    plot smallint NOT NULL,
    current_seed_sample char(6),
    PRIMARY KEY(lab_id, plot),
    CONSTRAINT valid_plot CHECK (
        plot BETWEEN 1
        AND 20
    )
);

CREATE TABLE IF NOT EXISTS lab_checks(
    date date NOT NULL,
    time time NOT NULL,
    lab_id char(1) NOT NULL REFERENCES labs(id),
    lab_tech_id smallint NOT NULL REFERENCES lab_techs(id),
    PRIMARY KEY(date, time, lab_id)
);

CREATE TABLE IF NOT EXISTS plot_checks(
    date date NOT NULL,
    time time NOT NULL,
    lab_id char(1) NOT NULL REFERENCES labs(id),
    plot smallint NOT NULL,
    PRIMARY KEY(date, time, lab_id, plot),
    FOREIGN KEY(date, time, lab_id) REFERENCES lab_checks(date, time, lab_id),
    FOREIGN KEY(lab_id, plot) REFERENCES plots(lab_id, plot),
    seed_sample char(6) NOT NULL,
    humidity numeric(4, 2) CHECK (
        humidity BETWEEN 0.5
        AND 52.0
    ),
    light numeric(5, 2) CHECK (
        light BETWEEN 0
        AND 100
    ),
    temperature numeric(4, 2) CHECK(
        temperature BETWEEN 4
        AND 40
    ),
    equipment_fault boolean NOT NULL,
    blossoms smallint NOT NULL CHECK (
        blossoms BETWEEN 0
        AND 1000
    ),
    plants smallint NOT NULL CHECK (
        plants BETWEEN 0
        AND 20
    ),
    fruit smallint NOT NULL CHECK (
        fruit BETWEEN 0
        AND 1000
    ),
    max_height numeric(6, 2) NOT NULL CHECK (
        max_height BETWEEN 0
        AND 1000
    ),
    min_height numeric(6, 2) NOT NULL CHECK (
        min_height BETWEEN 0
        AND 1000
    ),
    median_height numeric(6, 2) NOT NULL CHECK (
        median_height BETWEEN min_height
        AND max_height
    ),
    notes text
);

CREATE VIEW data_record_view AS (
    SELECT
        pc.date AS "Date",
        to_char(pc.time, 'FMHH24:MI') AS "Time",
        lt.name AS "Technician",
        pc.lab_id AS "Lab",
        pc.plot AS "Plot",
        pc.seed_sample AS "Seed sample",
        pc.humidity AS "Humidity",
        pc.light AS "Light",
        pc.temperature AS "Temperaturue",
        pc.plants AS "Plants",
        pc.blossoms AS "Blossoms",
        pc.fruit AS "Fruit",
        pc.max_height AS "Max Height",
        pc.min_height AS "Min Height",
        pc.median_height AS "Median Height",
        pc.notes AS "Notes"
    FROM
        plot_checks AS pc
        JOIN lab_checks AS lc ON pc.lab_id = lc.lab_id
        AND pc.date = lc.date
        AND pc.time = lc.time
        JOIN lab_techs AS lt ON lc.lab_tech_id = lt.id
);