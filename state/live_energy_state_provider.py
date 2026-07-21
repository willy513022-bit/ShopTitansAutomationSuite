from __future__ import annotations

from ai.game_state import (
    EnergyState,
    GameState,
)
from detectors.energy_detector import (
    EnergyDetector,
)


class LiveEnergyStateProvider:
    def __init__(
        self,
        detector: EnergyDetector | None = None,
        minimum_confidence: float = 0.20,
    ) -> None:
        self.detector = (
            detector
            or EnergyDetector()
        )
        self.minimum_confidence = (
            minimum_confidence
        )

    def apply(
        self,
        state: GameState,
    ) -> None:
        result = self.detector.detect(
            save_debug=True
        )

        recognized = result.recognized

        state.metadata[
            "live_energy_raw_text"
        ] = recognized.raw_text

        state.metadata[
            "live_energy_confidence"
        ] = recognized.confidence

        state.metadata[
            "live_energy_debug_image"
        ] = result.debug_image_path

        if not recognized.valid:
            state.metadata[
                "live_energy_error"
            ] = (
                "OCR 未能辨識有效能量值"
            )
            return

        if (
            recognized.confidence
            < self.minimum_confidence
        ):
            state.metadata[
                "live_energy_error"
            ] = (
                "OCR 信心值低於門檻"
            )
            return

        state.energy = EnergyState(
            current=recognized.current,
            maximum=recognized.maximum,
        )
