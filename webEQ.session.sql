DROP TABLE webEQ;
CREATE TABLE webEQ (
    ID int NOT NULL PRIMARY KEY,
    rawiem VARCHAR(255),
    iem VARCHAR(255),
    target VARCHAR(255),
    algo VARCHAR(20),
    processed DATETIME,
    filtercount INT,
    eqres VARCHAR(5),
    mode VARCHAR(20),
    results VARCHAR(2000)
    ); 
