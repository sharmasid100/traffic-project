from app.services.ocr import clean_plate_number


def test_clean_plate_number_strips_and_maps_lookalikes():
    assert clean_plate_number("mh-12 AB 1234") == "MH12A81234"
    assert clean_plate_number("OISB") == "0158"
    assert clean_plate_number("***") == ""
