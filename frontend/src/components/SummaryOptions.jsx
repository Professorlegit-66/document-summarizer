import { SUMMARY_LENGTH_OPTIONS, SUMMARY_STYLE_OPTIONS } from '../constants/summaryOptions';
import { FOCUS_RING } from '../constants/styles';

/**
 * Controlled selector for summary length and style.
 * Owns no state — length/style and their change handlers come from props.
 */
export default function SummaryOptions({ length, style, onLengthChange, onStyleChange }) {
  return (
    <div className="flex flex-col gap-6">
      <OptionGroup
        label="Summary Length"
        options={SUMMARY_LENGTH_OPTIONS}
        selectedValue={length}
        onSelect={onLengthChange}
      />
      <OptionGroup
        label="Summary Style"
        options={SUMMARY_STYLE_OPTIONS}
        selectedValue={style}
        onSelect={onStyleChange}
      />
    </div>
  );
}

function OptionGroup({ label, options, selectedValue, onSelect }) {
  return (
    <div>
      <p className="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">{label}</p>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => {
          const isSelected = option.value === selectedValue;
          return (
            <button
              key={option.value}
              type="button"
              onClick={() => onSelect(option.value)}
              aria-pressed={isSelected}
              className={`rounded-full border px-4 py-1.5 text-sm font-medium transition-colors ${FOCUS_RING}
                ${
                  isSelected
                    ? 'border-blue-600 bg-blue-600 text-white'
                    : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700'
                }`}
            >
              {option.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}