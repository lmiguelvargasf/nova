import datetime

from advanced_alchemy.types import DateTimeUTC
from sqlalchemy.orm import Mapped, declarative_mixin, mapped_column


@declarative_mixin
class SoftDeleteMixin:
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTimeUTC(timezone=True),
        default=None,
        index=True,
        sort_order=3004,
    )

    def soft_delete(self) -> None:
        self.deleted_at = datetime.datetime.now(datetime.UTC)
