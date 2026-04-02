const categories = ['all', '科技', '商业', '经济', '社会']

interface CategoryFilterProps {
  value: string
  onChange: (category: string) => void
}

export function CategoryFilter({ value, onChange }: CategoryFilterProps) {
  return (
    <div className="filter-row">
      {categories.map((category) => (
        <button
          key={category}
          className={`filter-btn ${value === category ? 'active' : ''}`}
          onClick={() => onChange(category)}
        >
          {category === 'all' ? '全部' : category}
        </button>
      ))}
    </div>
  )
}
