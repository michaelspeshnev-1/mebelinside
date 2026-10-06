// Шрифты: системные, чтобы работало без интернета и с кириллицей.
export const FONT = '"Inter", "Helvetica Neue", "Segoe UI", Arial, "DejaVu Sans", "Liberation Sans", sans-serif';

/** Масштаб интерфейса от меньшей стороны кадра: одинаково смотрится и 16:9, и 9:16. */
export const unit = (width, height) => Math.min(width, height) / 100;
