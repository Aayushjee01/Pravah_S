"""Tests for the data preprocessing pipeline."""

import pandas as pd
import pytest

from app.ml.preprocessing import (
    clean_bhk,
    clean_floor,
    clean_price,
    clean_yes_no,
    normalize_location,
)


class TestNormalizeLocation:
    """Tests for location normalization."""

    def test_valid_location_lowercase(self):
        assert normalize_location("kharghar") == "Kharghar"

    def test_valid_location_uppercase(self):
        assert normalize_location("KHARGHAR ") == "Kharghar"

    def test_location_with_spaces(self):
        assert normalize_location(" panvel") == "Panvel"

    def test_cbd_belapur(self):
        assert normalize_location("cbd belapur") == "CBD Belapur"

    def test_empty_string(self):
        assert normalize_location("") is None

    def test_none_value(self):
        assert normalize_location(None) is None

    def test_unknown_location(self):
        assert normalize_location("Mumbai") is None


class TestCleanPrice:
    """Tests for price cleaning."""

    def test_plain_integer(self):
        assert clean_price(15000000) == 15000000.0

    def test_inr_suffix(self):
        assert clean_price("15000000 INR") == 15000000.0

    def test_rupee_symbol(self):
        assert clean_price("₹15000000") == 15000000.0

    def test_negative_price(self):
        assert clean_price(-1000) is None

    def test_zero_price(self):
        assert clean_price(0) is None

    def test_none_value(self):
        assert clean_price(None) is None


class TestCleanBHK:
    """Tests for BHK cleaning."""

    def test_plain_number(self):
        assert clean_bhk(2) == 2

    def test_bhk_suffix(self):
        assert clean_bhk("2BHK") == 2

    def test_bhk_string(self):
        assert clean_bhk("3") == 3

    def test_out_of_range(self):
        assert clean_bhk(10) is None

    def test_none_value(self):
        assert clean_bhk(None) is None


class TestCleanFloor:
    """Tests for floor cleaning."""

    def test_ground_floor(self):
        assert clean_floor("Ground") == 0

    def test_numeric_floor(self):
        assert clean_floor(5) == 5

    def test_string_floor(self):
        assert clean_floor("10") == 10

    def test_none_value(self):
        assert clean_floor(None) is None

    def test_too_high(self):
        assert clean_floor(200) is None


class TestCleanYesNo:
    """Tests for yes/no cleaning."""

    def test_yes(self):
        assert clean_yes_no("Yes") == 1

    def test_no(self):
        assert clean_yes_no("No") == 0

    def test_yes_uppercase(self):
        assert clean_yes_no("YES") == 1

    def test_no_lowercase(self):
        assert clean_yes_no("no") == 0

    def test_none(self):
        assert clean_yes_no(None) is None
