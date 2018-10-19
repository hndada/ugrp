%csv_dir=input('enter the directory of folder which have csvs(with quotation mark):\n');
%fileList=dir(csv_dir);
filelist=dir('C:\Users\hndada\Documents\GitHub\ugrp\sdvx\csv_dir');

global kshlist decay_table lvl_class skipped
lvl_class=csvread('lvl_class.csv',0,1); %margin-included range of each level

decay=0.9;
decay_table=zeros(1000,1); %size '1000' is an arbitrary number
for i = 1:length(decay_table)
    decay_table(i,1)=decay^(i-1);
end

kshlist=struct();
failed=0;
skipped=0; %for counting the number of placeholder needed
for i = 1:length(filelist)
    filename=strcat(filelist(i).folder,'\',filelist(i).name);
    kshID=fopen(filename, 'rt');
    if kshID==-1 || filelist(i).bytes<150
        failed=failed+1;
        continue
    end
    %throw the charts out which level is less than 6 
    %{
    if cell2mat(textscan(kshID,'%d')) <= 6
       skipped=skipped+1;
       fclose(kshID);
       continue
    end
    %}
    fseek(kshID,0,'bof');
    kshlist(i-failed-skipped).name=filelist(i).name;
    kshlist(i-failed-skipped).level=textscan(kshID,'%d');
    kshlist(i-failed-skipped).csv=csvread(filename, 2,1);
    fclose(kshID);
end
kshlist=kshlist.';

%temporary test about feature quality
%{
correct=zeros(500,1);
w_list=zeros(500,4);
for iter=1:size(correct)
    w=[1,0,0,0];
    w(2:end)=rand(1,3);
    correct(iter)=1-w_ga(w); %the number of correctness
    w_list(iter,:)=w;
end
disp(max(correct));
%}

%constraint of genetic function: 0<=w(i)<=1
A= [eye(4);-eye(4)];
b= [ones(4,1);zeros(4,1)];
lb=[0,0,0,0];
ub=ones(4,1);
options=optimoptions('ga','MaxGenerations',50);
w_best=ga(@w_ga,4,[],[],[],[],lb,ub,[],options);

disp(1-w_ga(w_best)) %show how much correct the selected best weight is

function w_missrate = w_ga ( w ) 
    global kshlist decay_table lvl_class skipped
    diff_score=zeros(length(kshlist),1);
    for i=1:length(kshlist)
        section_score=w*kshlist(i).csv';
        ss_sort=sort(section_score,'descend');
        diff_score(i)=ss_sort*decay_table(1:length(ss_sort));
    end
    wrong_count=0;
    for i = 1:length(kshlist)
        %prctile(diff_score,100-lvl_class(21-cell2mat(kshlist(i).level),1))
        if diff_score(i) < prctile([zeros(skipped,1);diff_score],lvl_class(cell2mat(kshlist(i).level),1)) ...
        || diff_score(i) > prctile([zeros(skipped,1);diff_score],lvl_class(cell2mat(kshlist(i).level),2))
            wrong_count=wrong_count+1;
        end
    end
    w_missrate=wrong_count/length(kshlist);  
end
