void ReferenceSpectrumSession::begin(const QVariantMap& values) {
    KumoAudio::SpectrumRequest r;
    const auto path=values.value("path").toString();
    r.path=QUrl(path).isLocalFile()?QUrl(path).toLocalFile():path;
    r.fromMs=values.value("from",0).toDouble();r.untilMs=values.value("until",8000).toDouble();
    r.columns=values.value("columns",512).toInt();r.rows=values.value("rows",352).toInt();
    r.fftSize=values.value("fftSize",16384).toInt();
    r.lowPitch=values.value("lowPitch",20.5).toDouble();r.highPitch=values.value("highPitch",108.5).toDouble();
    r.tuning=values.value("tuning",440).toDouble();
    const auto issue=KumoAudio::validateSpectrumRequest(r);
    if(!issue.isEmpty()) {_tile={};_tile.error=issue;_publishedPath=r.path;_status=issue;emit changed();return;}
    _busy=true;_backgroundBusy=false;_preparedBlocks=0;_totalBlocks=0;
    _status=tr("正在准备这一段的频谱…");emit changed();
    _cancel=std::make_shared<std::atomic_bool>(false);
    const auto cancelled=_cancel;const auto version=_generation;const auto directory=_directory;
    const int diskMiB=_diskMiB;
    const bool refresh=values.value("refresh",false).toBool(),preload=values.value("preload",false).toBool();
    const double fundamentalMix=qBound(0.,values.value("fundamentalMix",0.).toDouble(),1.);
    QtConcurrent::run(&_pool,[this,r,version,cancelled,directory,diskMiB,refresh,preload,fundamentalMix] {
        QThread::currentThread()->setPriority(QThread::LowPriority);
        QElapsedTimer clock;clock.start();
        constexpr double blockMs=4000.;
        const int first=int(std::floor(r.fromMs/blockMs)),last=int(std::ceil(r.untilMs/blockMs))-1;
        const int count=last-first+1;
        auto load=[&](int index,bool force,bool& found) {
            const auto raw=KumoAudio::spectrumBlock(r,index);
            const auto key=KumoAudio::spectrumKey(raw);
            KumoAudio::SpectrumTile block;found=false;
            if(!force) {QMutexLocker lock(&_memoryMutex);if(auto item=_memory.object(key)){block=*item;found=true;}}
            if(!found&&!force&&diskMiB)found=readCache(cachePath(directory,key),&block);
            if(found && (block.image.format()!=QImage::Format_Grayscale8 || block.image.width()!=raw.columns ||
               block.image.height()!=raw.rows || block.lowPitch!=raw.lowPitch || block.highPitch!=raw.highPitch ||
               block.fromMs!=raw.fromMs || block.untilMs!=raw.untilMs || block.sampleRate<=0))found=false;
            if(!found)block=KumoAudio::spectrum(raw,*cancelled);
            if(*cancelled || !block.error.isEmpty() || block.image.isNull())return block;
            if(!found)writeCache(directory,key,block,diskMiB);
            {QMutexLocker lock(&_memoryMutex);if(!*cancelled)_memory.insert(key,new KumoAudio::SpectrumTile(block),qMax(1,int(qint64(block.image.bytesPerLine())*block.image.height()/1024)));}
            return block;
        };
        KumoAudio::SpectrumTile tile;tile.fromMs=r.fromMs;tile.untilMs=r.untilMs;tile.lowPitch=r.lowPitch;tile.highPitch=r.highPitch;
        tile.image=QImage(r.columns,r.rows,QImage::Format_Grayscale8);tile.image.fill(0);
        int computed=0,cached=0,completed=0;
        for(int index=first;index<=last && !*cancelled;++index) {
            bool found=false;auto block=load(index,refresh,found);
            if(*cancelled)break;
            if(!block.error.isEmpty()){tile.error=block.error;break;}
            if(block.image.isNull()){tile.error=tr("这一段的频谱尚未生成，请重新分析。");break;}
            if(found)++cached;else ++computed;
            tile.durationMs=block.durationMs;tile.sampleRate=block.sampleRate;
            if(fundamentalMix>0) {
                const auto key=KumoAudio::spectrumKey(KumoAudio::spectrumBlock(r,index))+":fundamental:"+QString::number(qRound(fundamentalMix*1000));
                bool filtered=false;
                if(!refresh){QMutexLocker lock(&_memoryMutex);if(auto prior=_memory.object(key)){block=*prior;filtered=true;}}
                if(!filtered) {
                    block.image=KumoAudio::emphasizeFundamental(block,fundamentalMix,*cancelled);
                    if(!*cancelled){QMutexLocker lock(&_memoryMutex);_memory.insert(key,new KumoAudio::SpectrumTile(block),qMax(1,int(qint64(block.image.bytesPerLine())*block.image.height()/1024)));}
                }
            }
            KumoAudio::projectSpectrumBlock(r,block,tile.image,*cancelled);++completed;
            QMetaObject::invokeMethod(this,[this,version,completed,count] {
                if(version!=_generation)return;
                _status=tr("频谱已准备 %1 / %2 段").arg(completed).arg(count);emit changed();
            },Qt::QueuedConnection);
        }
        if(!tile.error.isEmpty() || completed!=count)tile.image={};
        const auto elapsed=clock.elapsed();
        const int total=tile.durationMs>0?int(std::ceil(tile.durationMs/blockMs)):0;
        const bool background=preload && total>0 && tile.error.isEmpty() && !tile.image.isNull() && !*cancelled;
        QMetaObject::invokeMethod(this,[this,tile,version,cancelled,elapsed,computed,cached,count,background,total,path=r.path] {
            _busy=false;
            if(version!=_generation && _pending.isEmpty())_status=tr("频谱分析已停止，已有结果保留。");
            if(version==_generation && !*cancelled) {
                _elapsedMs=computed?elapsed:0;_workerMs=elapsed;_computedBlocks=computed;_cachedBlocks=cached;_requestedBlocks=count;
                _backgroundBusy=background;_totalBlocks=total;_preparedBlocks=qMin(total,count);
                _tile=tile;_publishedPath=path;
                _status=tile.error.isEmpty()?tr("频谱已更新 · %1 段复用，%2 段新分析").arg(cached).arg(computed):tile.error;
            }
            emit changed();
            if(!_pending.isEmpty()){const auto next=_pending;_pending.clear();begin(next);}
        },Qt::QueuedConnection);
        if(!background)return;
        int ready=qMax(0,qMin(last,total-1)-qMax(first,0)+1),fresh=0;
        QElapsedTimer notification;notification.start();QString backgroundError;
        auto prepare=[&](int index) {
            if(index<0 || index>=total || (index>=first&&index<=last) || *cancelled)return;
            bool found=false;const auto block=load(index,refresh,found);
            if(*cancelled)return;
            if(!block.error.isEmpty() || block.image.isNull()){backgroundError=block.error.isEmpty()?tr("这一段音频未能读取。"):block.error;*cancelled=true;return;}
            ++ready;if(!found)++fresh;
            if(notification.elapsed()>=250) {
                notification.restart();
                QMetaObject::invokeMethod(this,[this,version,ready,total] {
                    if(version!=_generation)return;
                    _preparedBlocks=ready;_status=tr("频谱可用 · 后台准备 %1 / %2 段").arg(ready).arg(total);emit changed();
                },Qt::QueuedConnection);
            }
        };
        prepare(first-1);prepare(last+1);
        // Keep only a block and the bounded image cache while preparing a long recording.
        for(int index=0;index<total && !*cancelled;++index)
            if(index!=first-1 && index!=last+1)prepare(index);
        QMetaObject::invokeMethod(this,[this,version,cancelled,ready,total,fresh,backgroundError] {
            if(version!=_generation)return;
            _backgroundBusy=false;_preparedBlocks=ready;_backgroundComputed=fresh;
            if(!backgroundError.isEmpty())_status=tr("当前频谱可用；后台准备暂停：%1").arg(backgroundError);
            else if(!*cancelled)_status=tr("整条录音的频谱已准备好 · %1 段").arg(total);
            emit changed();
        },Qt::QueuedConnection);
    });
}
