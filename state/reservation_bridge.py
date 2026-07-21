from __future__ import annotations

from dataclasses import dataclass, field

from models.quality import Quality


@dataclass(frozen=True)
class Reservation:
    item_id: str
    quality: Quality
    quantity: int
    reason: str


@dataclass
class ReservationBook:
    reservations: list[Reservation] = field(
        default_factory=list
    )

    def reserve(
        self,
        item_id: str,
        quality: Quality,
        quantity: int,
        reason: str,
    ) -> None:
        self.reservations.append(
            Reservation(
                item_id=item_id,
                quality=quality,
                quantity=quantity,
                reason=reason,
            )
        )

    def reserved_quantity(
        self,
        item_id: str,
        quality: Quality,
    ) -> int:
        return sum(
            reservation.quantity
            for reservation in self.reservations
            if reservation.item_id == item_id
            and reservation.quality == quality
        )

    def can_sell(
        self,
        item_id: str,
        quality: Quality,
        current_quantity: int,
        requested_quantity: int = 1,
    ) -> bool:
        reserved = self.reserved_quantity(
            item_id,
            quality,
        )

        available = (
            current_quantity
            - reserved
        )

        return available >= requested_quantity
