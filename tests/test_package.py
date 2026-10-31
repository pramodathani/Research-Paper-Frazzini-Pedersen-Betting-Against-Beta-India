"""Checks that the study's package imports."""

import frazzini_pedersen_betting_against_beta_india


class TestPackage:
    """Tests that the package and its subpackages can be imported."""

    def test_package_has_docstring(self) -> None:
        """Checks that the package imports and documents itself.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If the package has no docstring.
        """
        package = frazzini_pedersen_betting_against_beta_india
        assert package.__doc__ is not None
