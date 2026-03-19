"""Comprehensive tests for PriceResult and PriceStep dataclasses.

These tests verify construction, float backward-compatibility, comparison
operators, arithmetic operators, Decimal handling, boolean truthiness, and
string representation.  They do NOT require an RPC connection.
"""

from decimal import Decimal

import pytest

from y.datatypes import PriceResult, PriceStep, UsdPrice


# ---------------------------------------------------------------------------
# PriceStep tests
# ---------------------------------------------------------------------------


class TestPriceStep:
    """Tests for the PriceStep dataclass."""

    def test_construction(self):
        step = PriceStep(
            token="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            price=UsdPrice(1800.0),
            source="Chainlink ETH/USD feed 0x5f4e...",
        )
        assert step.token == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
        assert step.price == UsdPrice(1800.0)
        assert step.source == "Chainlink ETH/USD feed 0x5f4e..."

    def test_repr(self):
        step = PriceStep(
            token="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            price=UsdPrice(1800.0),
            source="Chainlink ETH/USD",
        )
        r = repr(step)
        assert "PriceStep" in r
        assert "Chainlink ETH/USD" in r

    def test_equality(self):
        a = PriceStep(token="0xA", price=UsdPrice(1.0), source="src")
        b = PriceStep(token="0xA", price=UsdPrice(1.0), source="src")
        assert a == b

    def test_inequality(self):
        a = PriceStep(token="0xA", price=UsdPrice(1.0), source="src")
        b = PriceStep(token="0xB", price=UsdPrice(1.0), source="src")
        assert a != b


# ---------------------------------------------------------------------------
# PriceResult – construction and attribute access
# ---------------------------------------------------------------------------


class TestPriceResultConstruction:
    """Tests for PriceResult construction and attribute access."""

    def test_basic_construction(self):
        result = PriceResult(price=UsdPrice(1234.56), path=[])
        assert result.price == UsdPrice(1234.56)
        assert result.path == []

    def test_construction_with_path(self):
        step = PriceStep(token="0xA", price=UsdPrice(10.0), source="test source")
        result = PriceResult(price=UsdPrice(10.0), path=[step])
        assert len(result.path) == 1
        assert result.path[0].source == "test source"

    def test_construction_with_multi_step_path(self):
        steps = [
            PriceStep(token="0xA", price=UsdPrice(1800.0), source="Chainlink ETH/USD"),
            PriceStep(token="0xB", price=UsdPrice(1.0), source="Stablecoin DAI"),
        ]
        result = PriceResult(price=UsdPrice(1800.0), path=steps)
        assert len(result.path) == 2
        assert result.path[0].token == "0xA"
        assert result.path[1].token == "0xB"


# ---------------------------------------------------------------------------
# PriceResult – float compatibility
# ---------------------------------------------------------------------------


class TestPriceResultFloatCompat:
    """Tests for PriceResult backward-compatibility with float."""

    def test_float_conversion(self):
        result = PriceResult(price=UsdPrice(1234.56), path=[])
        assert float(result) == 1234.56
        assert isinstance(float(result), float)

    def test_float_of_zero(self):
        result = PriceResult(price=UsdPrice(0), path=[])
        assert float(result) == 0.0

    def test_float_negative(self):
        result = PriceResult(price=UsdPrice(-5.0), path=[])
        assert float(result) == -5.0


# ---------------------------------------------------------------------------
# PriceResult – comparison operators
# ---------------------------------------------------------------------------


class TestPriceResultComparison:
    """Tests for PriceResult comparison operators."""

    def test_gt(self):
        result = PriceResult(price=UsdPrice(100.0), path=[])
        assert result > 0
        assert result > 99.9
        assert not (result > 100.0)
        assert not (result > 200.0)

    def test_lt(self):
        result = PriceResult(price=UsdPrice(100.0), path=[])
        assert result < 200.0
        assert result < 100.1
        assert not (result < 100.0)
        assert not (result < 50.0)

    def test_ge(self):
        result = PriceResult(price=UsdPrice(100.0), path=[])
        assert result >= 100.0
        assert result >= 99.0
        assert not (result >= 101.0)

    def test_le(self):
        result = PriceResult(price=UsdPrice(100.0), path=[])
        assert result <= 100.0
        assert result <= 101.0
        assert not (result <= 99.0)

    def test_eq_numeric(self):
        result = PriceResult(price=UsdPrice(100.0), path=[])
        assert result == 100.0
        assert result == 100
        assert not (result == 99.0)

    def test_eq_price_result(self):
        a = PriceResult(price=UsdPrice(100.0), path=[])
        b = PriceResult(price=UsdPrice(100.0), path=[])
        assert a == b

    def test_eq_price_result_different_paths(self):
        step = PriceStep(token="0xA", price=UsdPrice(100.0), source="src")
        a = PriceResult(price=UsdPrice(100.0), path=[])
        b = PriceResult(price=UsdPrice(100.0), path=[step])
        # Two PriceResults with same price but different paths are NOT equal
        assert a != b

    def test_comparison_with_int(self):
        result = PriceResult(price=UsdPrice(5.0), path=[])
        assert result > 4
        assert result < 6
        assert result >= 5
        assert result <= 5


# ---------------------------------------------------------------------------
# PriceResult – arithmetic operators
# ---------------------------------------------------------------------------


class TestPriceResultArithmetic:
    """Tests for PriceResult arithmetic operators."""

    def test_mul(self):
        result = PriceResult(price=UsdPrice(100.0), path=[])
        assert result * 2 == 200.0
        assert result * 0.5 == 50.0

    def test_rmul(self):
        result = PriceResult(price=UsdPrice(100.0), path=[])
        assert 2 * result == 200.0
        assert 0.5 * result == 50.0

    def test_truediv(self):
        result = PriceResult(price=UsdPrice(100.0), path=[])
        assert result / 2 == 50.0
        assert result / 4 == 25.0

    def test_rtruediv(self):
        result = PriceResult(price=UsdPrice(100.0), path=[])
        assert 200.0 / result == 2.0
        assert 1.0 / result == 0.01

    def test_add(self):
        result = PriceResult(price=UsdPrice(100.0), path=[])
        assert result + 50 == 150.0
        assert result + 0.5 == 100.5

    def test_radd(self):
        result = PriceResult(price=UsdPrice(100.0), path=[])
        assert 50 + result == 150.0
        assert 0.5 + result == 100.5

    def test_sub(self):
        result = PriceResult(price=UsdPrice(100.0), path=[])
        assert result - 30 == 70.0
        assert result - 100 == 0.0

    def test_rsub(self):
        result = PriceResult(price=UsdPrice(100.0), path=[])
        assert 200 - result == 100.0

    def test_arithmetic_returns_float(self):
        """Arithmetic operations return plain float, not PriceResult."""
        result = PriceResult(price=UsdPrice(100.0), path=[])
        assert isinstance(result * 2, float)
        assert isinstance(result + 1, float)
        assert isinstance(result - 1, float)
        assert isinstance(result / 2, float)


# ---------------------------------------------------------------------------
# PriceResult – Decimal handling
# ---------------------------------------------------------------------------


class TestPriceResultDecimal:
    """Tests for Decimal compatibility."""

    def test_decimal_of_price_works(self):
        """Decimal(result.price) should succeed."""
        result = PriceResult(price=UsdPrice(1234.56), path=[])
        d = Decimal(result.price)
        assert isinstance(d, Decimal)
        assert float(d) == pytest.approx(1234.56)

    def test_decimal_of_result_raises(self):
        """Decimal(result) should raise TypeError - callers must use result.price."""
        result = PriceResult(price=UsdPrice(1234.56), path=[])
        with pytest.raises(TypeError):
            Decimal(result)


# ---------------------------------------------------------------------------
# PriceResult – boolean truthiness
# ---------------------------------------------------------------------------


class TestPriceResultBool:
    """Tests for PriceResult boolean truthiness."""

    def test_truthy_positive_price(self):
        result = PriceResult(price=UsdPrice(100.0), path=[])
        assert bool(result) is True
        assert result  # if result: ...

    def test_falsy_zero_price(self):
        result = PriceResult(price=UsdPrice(0), path=[])
        assert bool(result) is False
        assert not result

    def test_truthy_negative_price(self):
        result = PriceResult(price=UsdPrice(-5.0), path=[])
        assert bool(result) is True

    def test_truthy_small_price(self):
        result = PriceResult(price=UsdPrice(0.0001), path=[])
        assert bool(result) is True


# ---------------------------------------------------------------------------
# PriceResult – string representation
# ---------------------------------------------------------------------------


class TestPriceResultRepr:
    """Tests for PriceResult string representation."""

    def test_repr_empty_path(self):
        result = PriceResult(price=UsdPrice(1234.56), path=[])
        r = repr(result)
        assert "PriceResult" in r
        assert "1234.56" in r

    def test_repr_with_path(self):
        step = PriceStep(token="0xA", price=UsdPrice(10.0), source="test")
        result = PriceResult(price=UsdPrice(10.0), path=[step])
        r = repr(result)
        assert "PriceResult" in r
        assert "1 step" in r or "1" in r

    def test_repr_multi_step_path(self):
        steps = [
            PriceStep(token="0xA", price=UsdPrice(1800.0), source="Chainlink"),
            PriceStep(token="0xB", price=UsdPrice(1.0), source="Stablecoin"),
        ]
        result = PriceResult(price=UsdPrice(1800.0), path=steps)
        r = repr(result)
        assert "PriceResult" in r
        assert "2 step" in r or "2" in r


# ---------------------------------------------------------------------------
# PriceResult – hash
# ---------------------------------------------------------------------------


class TestPriceResultHash:
    """Tests for PriceResult hashing."""

    def test_hashable(self):
        result = PriceResult(price=UsdPrice(100.0), path=[])
        # Should not raise
        h = hash(result)
        assert isinstance(h, int)

    def test_can_be_dict_key(self):
        result = PriceResult(price=UsdPrice(100.0), path=[])
        d = {result: "test"}
        assert d[result] == "test"


# ---------------------------------------------------------------------------
# PriceResult – abs
# ---------------------------------------------------------------------------


class TestPriceResultAbs:
    """Tests for PriceResult abs() support."""

    def test_abs_positive(self):
        result = PriceResult(price=UsdPrice(100.0), path=[])
        assert abs(result) == 100.0

    def test_abs_negative(self):
        result = PriceResult(price=UsdPrice(-100.0), path=[])
        assert abs(result) == 100.0
