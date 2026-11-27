/**
 * Ограничение ввода в полях с атрибутом data-input.
 *
 * Виды ввода (выставляются в main/input_rules.py):
 *   integer        - только цифры;
 *   decimal        - цифры и одна точка, не больше data-decimal-places знаков после неё;
 *   signed_decimal - то же, но можно минус в начале;
 *   letters        - только буквы, пробел, дефис, апостроф;
 *   phone          - цифры, + в начале, пробел, скобки, дефис;
 *   card           - латинские буквы, цифры, дефис.
 *
 * Если новое значение не подходит под правило, поле откатывается к последнему
 * корректному значению - так отсекаются и нажатия клавиш, и вставка, и перетаскивание.
 * Запятая в числах сама меняется на точку.
 */
(function () {
    const SIMPLE_RULES = {
        integer: /^\d*$/,
        letters: /^[A-Za-zА-Яа-яЁё\s'-]*$/,
        phone: /^\+?[\d\s()-]*$/,
        card: /^[A-Za-z0-9-]*$/,
    };

    /** Регулярка для десятичного числа с учётом max_digits и decimal_places поля. */
    function getDecimalPattern(input, allowNegative) {
        const maxDigits = Number(input.dataset.maxDigits) || 20;
        const decimalPlaces = Number(input.dataset.decimalPlaces);
        const places = Number.isNaN(decimalPlaces) ? 10 : decimalPlaces;
        const sign = allowNegative ? '-?' : '';
        const fraction = places > 0 ? `([.]\\d{0,${places}})?` : '';
        return new RegExp(`^${sign}\\d{0,${maxDigits - places}}${fraction}$`);
    }

    function getPattern(input) {
        const rule = input.dataset.input;
        if (rule === 'decimal') {
            return getDecimalPattern(input, false);
        }
        if (rule === 'signed_decimal') {
            return getDecimalPattern(input, true);
        }
        return SIMPLE_RULES[rule];
    }

    function normalize(input, value) {
        if (input.dataset.input.endsWith('decimal')) {
            return value.replaceAll(',', '.');
        }
        return value;
    }

    function bindInput(input) {
        const pattern = getPattern(input);
        if (!pattern) {
            return;
        }

        let lastValue = input.value;

        input.addEventListener('input', function () {
            const caret = input.selectionStart;
            const value = normalize(input, input.value);

            // Старое значение из БД может не подходить под правило -
            // тогда даём хотя бы стирать символы, чтобы его можно было исправить.
            const isErasingInvalid = !pattern.test(lastValue) && value.length < lastValue.length;

            if (pattern.test(value) || isErasingInvalid) {
                if (value !== input.value) {
                    input.value = value;
                    input.setSelectionRange(caret, caret);
                }
                lastValue = value;
                return;
            }

            const restoredCaret = Math.max(0, caret - (input.value.length - lastValue.length));
            input.value = lastValue;
            input.setSelectionRange(restoredCaret, restoredCaret);
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('[data-input]').forEach(bindInput);
    });
})();
