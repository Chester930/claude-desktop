import { Component, EventEmitter, Output, computed } from '@angular/core';
import { SettingsService } from '../../settings.service';

@Component({
  selector: 'app-recent-work-dirs',
  standalone: true,
  templateUrl: './recent-work-dirs.html',
})
export class RecentWorkDirsComponent {
  @Output() select = new EventEmitter<string>();

  recentWorkDirs = computed(() => this.settings.get().recentWorkDirs);

  constructor(private settings: SettingsService) {}
}
