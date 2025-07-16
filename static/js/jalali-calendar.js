// Modern Compact Jalali Calendar Implementation
class JalaliCalendar {
    constructor() {
        this.monthNames = [
            'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
            'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
        ];
        
        this.dayNames = ['ش', 'ی', 'د', 'س', 'چ', 'پ', 'ج'];
        
        this.currentDate = new Date();
        this.selectedInput = null;
        this.calendar = null;
        
        this.init();
    }
    
    init() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('jalali-date')) {
                this.showCalendar(e.target);
            } else if (!e.target.closest('.jalali-calendar')) {
                this.hideCalendar();
            }
        });
    }
    
    showCalendar(input) {
        this.selectedInput = input;
        this.hideCalendar();
        
        const container = input.closest('.jalali-date-container');
        if (!container) return;
        
        this.calendar = this.createCalendar();
        container.appendChild(this.calendar);
        
        // Parse current value or use today
        const currentValue = input.value;
        if (currentValue && currentValue.match(/^\d{4}\/\d{1,2}\/\d{1,2}$/)) {
            const parts = currentValue.split('/');
            this.displayMonth(parseInt(parts[0]), parseInt(parts[1]));
        } else {
            const today = this.gregorianToJalali(new Date());
            this.displayMonth(today.year, today.month);
        }
    }
    
    hideCalendar() {
        if (this.calendar) {
            this.calendar.remove();
            this.calendar = null;
        }
    }
    
    createCalendar() {
        const calendar = document.createElement('div');
        calendar.className = 'jalali-calendar';
        
        calendar.innerHTML = `
            <div class="jalali-calendar-header">
                <button type="button" class="jalali-calendar-nav" data-action="prev-month">‹</button>
                <div class="jalali-calendar-title"></div>
                <button type="button" class="jalali-calendar-nav" data-action="next-month">›</button>
            </div>
            <div class="jalali-calendar-weekdays">
                ${this.dayNames.map(day => `<div class="jalali-calendar-weekday">${day}</div>`).join('')}
            </div>
            <div class="jalali-calendar-grid"></div>
        `;
        
        calendar.addEventListener('click', (e) => {
            const action = e.target.dataset.action;
            if (action === 'prev-month') {
                this.navigateMonth(-1);
            } else if (action === 'next-month') {
                this.navigateMonth(1);
            } else if (e.target.classList.contains('jalali-calendar-cell') && !e.target.classList.contains('other-month')) {
                this.selectDate(e.target);
            }
        });
        
        return calendar;
    }
    
    displayMonth(year, month) {
        this.currentYear = year;
        this.currentMonth = month;
        
        const title = this.calendar.querySelector('.jalali-calendar-title');
        title.textContent = `${this.monthNames[month - 1]} ${year}`;
        
        const grid = this.calendar.querySelector('.jalali-calendar-grid');
        grid.innerHTML = '';
        
        const firstDay = this.getFirstDayOfMonth(year, month);
        const daysInMonth = this.getDaysInMonth(year, month);
        const daysInPrevMonth = this.getDaysInMonth(year, month - 1);
        
        // Previous month's days
        for (let i = firstDay - 1; i >= 0; i--) {
            const day = daysInPrevMonth - i;
            const cell = this.createDayCell(day, true);
            grid.appendChild(cell);
        }
        
        // Current month's days
        for (let day = 1; day <= daysInMonth; day++) {
            const cell = this.createDayCell(day, false);
            grid.appendChild(cell);
        }
        
        // Next month's days to fill the grid
        const totalCells = grid.children.length;
        const remainingCells = 42 - totalCells; // 6 rows × 7 days
        for (let day = 1; day <= remainingCells && day <= 14; day++) {
            const cell = this.createDayCell(day, true);
            grid.appendChild(cell);
        }
    }
    
    createDayCell(day, otherMonth) {
        const cell = document.createElement('div');
        cell.className = 'jalali-calendar-cell';
        cell.textContent = day;
        
        if (otherMonth) {
            cell.classList.add('other-month');
        } else {
            cell.dataset.day = day;
            
            // Check if it's today
            const today = this.gregorianToJalali(new Date());
            if (this.currentYear === today.year && 
                this.currentMonth === today.month && 
                day === today.day) {
                cell.classList.add('today');
            }
            
            // Check if it's selected
            if (this.selectedInput && this.selectedInput.value) {
                const selectedDate = this.selectedInput.value;
                const expectedDate = `${this.currentYear}/${this.currentMonth}/${day}`;
                if (selectedDate === expectedDate) {
                    cell.classList.add('selected');
                }
            }
        }
        
        return cell;
    }
    
    selectDate(cell) {
        const day = parseInt(cell.dataset.day);
        const dateString = `${this.currentYear}/${this.currentMonth}/${day}`;
        
        if (this.selectedInput) {
            this.selectedInput.value = dateString;
            this.selectedInput.dispatchEvent(new Event('change'));
        }
        
        this.hideCalendar();
    }
    
    navigateMonth(direction) {
        let newMonth = this.currentMonth + direction;
        let newYear = this.currentYear;
        
        if (newMonth < 1) {
            newMonth = 12;
            newYear--;
        } else if (newMonth > 12) {
            newMonth = 1;
            newYear++;
        }
        
        this.displayMonth(newYear, newMonth);
    }
    
    getFirstDayOfMonth(year, month) {
        // Convert to Gregorian and get day of week
        const gregorian = this.jalaliToGregorian(year, month, 1);
        const dayOfWeek = gregorian.getDay();
        
        // Convert to Persian week (Saturday = 0)
        return (dayOfWeek + 1) % 7;
    }
    
    getDaysInMonth(year, month) {
        if (month < 1) {
            year--;
            month = 12;
        } else if (month > 12) {
            year++;
            month = 1;
        }
        
        if (month <= 6) {
            return 31;
        } else if (month <= 11) {
            return 30;
        } else {
            return this.isLeapYear(year) ? 30 : 29;
        }
    }
    
    isLeapYear(year) {
        const a = year + 1595;
        const b = Math.floor(a / 33);
        const c = a % 33;
        return c !== 0 && (c <= 28 || (c >= 30 && c <= 32));
    }
    
    jalaliToGregorian(jy, jm, jd) {
        const epyear = jy - ((jy >= 0) ? 979 : 980);
        const epochday = 365 * epyear + Math.floor(epyear / 33) * 8 + Math.floor(((epyear % 33) + 3) / 4);
        const auxmonth = (jm < 7) ? jm : jm + 1;
        const aux = (auxmonth < 7) ? 0 : auxmonth - 7;
        const epochday2 = epochday + ((jm - 1) * 30) + ((auxmonth < 7) ? 0 : 6) + jd - 1;
        const gyear = 400 * Math.floor(epochday2 / 146097) + 1;
        const gday = epochday2 % 146097;
        const year2 = 100 * Math.floor(gday / 36524) + gyear;
        const day2 = gday % 36524;
        const year3 = 4 * Math.floor(day2 / 1461) + year2;
        const day3 = day2 % 1461;
        const year4 = Math.floor(day3 / 365) + year3;
        const day4 = day3 % 365;
        
        return new Date(year4 + 621, 0, day4 + 79);
    }
    
    gregorianToJalali(date) {
        const gy = date.getFullYear();
        const gm = date.getMonth() + 1;
        const gd = date.getDate();
        
        const g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
        
        let jy, gy2;
        if (gy <= 1600) {
            jy = 0;
            gy2 = gy - 621;
        } else {
            jy = 979;
            gy2 = gy - 1600;
        }
        
        let days = 365 * gy2 + Math.floor((gy2 + 3) / 4) - Math.floor((gy2 + 99) / 100) + Math.floor((gy2 + 399) / 400) - 80 + gd;
        
        if (gm > 2) days += g_d_m[gm - 1];
        if ((gm > 2) && ((gy % 4 === 0 && gy % 100 !== 0) || (gy % 400 === 0))) days++;
        
        let jy2 = -14;
        let jp = days;
        
        do {
            jy2++;
            jp = days - 365 * jy2 - Math.floor(jy2 / 33) * 8 - Math.floor(((jy2 % 33) + 3) / 4);
        } while (jp >= 365);
        
        const jy3 = jy2 + jy + 1;
        const jp2 = jp + 1;
        
        let jm2, jd2;
        if (jp2 <= 186) {
            jm2 = 1 + Math.floor(jp2 / 31);
            jd2 = 1 + (jp2 % 31);
        } else {
            jm2 = 7 + Math.floor((jp2 - 186) / 30);
            jd2 = 1 + ((jp2 - 186) % 30);
        }
        
        return { year: jy3, month: jm2, day: jd2 };
    }
}

// Initialize calendar when page loads
document.addEventListener('DOMContentLoaded', function() {
    const calendar = new JalaliCalendar();
    
    // Set current Persian date for empty date inputs
    const today = calendar.gregorianToJalali(new Date());
    const todayString = `${today.year}/${today.month}/${today.day}`;
    
    document.querySelectorAll('.jalali-date').forEach(input => {
        if (!input.value) {
            input.value = todayString;
        }
    });
});