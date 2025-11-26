REATE DATABASE IF NOT EXISTS barriers;
USE barriers;

CREATE TABLE IF NOT EXISTS barrier (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        latitude VARCHAR(255),
        longitude VARCHAR(255),
        firmware VARCHAR(255),
        software VARCHAR(255),
        modem VARCHAR(255),
        ip VARCHAR(15),
        fqdn VARCHAR(255));

INSERT INTO barrier (name, latitude, longitude, firmware, software, modem, ip, fqdn) VALUES
        ('Barrier 1', 45.516294, -73.769440, '2025.10', '2025.08-01', 'LTE V2.4.1', '28.30.1.10', 'barrier1.mtq.versilis.com'),
        ('Barrier 2', 45.597944, -73.644889, '2025.11', '2025.11', '5G V1.2.1', '124.45.3.24', 'barrier2.pjc.versilis.com'),
        ('Barrier 3', 43.616242, -79.535076, '2024.03', '2023.06-02', 'LTE V3.4.2', '76.21.19.4', 'barrier3.mto.versilis.com');
